import json
import unittest
from unittest import mock

from ansible.compat.tests.mock import mock_open, patch
from ansible.module_utils.six import BytesIO, PY3
from ansible.module_utils.six.moves.urllib.error import HTTPError

from httpapi_plugins.ftd import HttpApi
from module_utils.fdm_swagger_client import OPERATIONS, MODELS, FdmSwaggerParser
from module_utils.http import HTTPMethod

if PY3:
    BUILTINS_NAME = 'builtins'
else:
    BUILTINS_NAME = '__builtin__'


class TestFtdHttpApi(unittest.TestCase):

    def setUp(self):
        self.connection_mock = mock.Mock()
        self.ftd_plugin = HttpApi(self.connection_mock)
        self.ftd_plugin.access_token = 'ACCESS_TOKEN'

    def test_login_should_update_token_info(self):
        self.ftd_plugin.access_token = False
        self.connection_mock.send.return_value = self._connection_response(
            {'access_token': 'ACCESS_TOKEN', 'refresh_token': 'REFRESH_TOKEN'}
        )

        self.ftd_plugin.login('foo', 'bar')

        assert 'ACCESS_TOKEN' == self.ftd_plugin.access_token
        assert 'REFRESH_TOKEN' == self.ftd_plugin.refresh_token

    def test_send_request_should_send_correct_request(self):
        exp_resp = {'id': '123', 'name': 'foo'}
        self.connection_mock.send.return_value = self._connection_response(exp_resp)

        resp = self.ftd_plugin.send_request('/test/{objId}', HTTPMethod.PUT,
                                            body_params={'name': 'foo'},
                                            path_params={'objId': '123'},
                                            query_params={'at': 0})

        assert exp_resp == resp
        self.connection_mock.send.assert_called_once_with('/test/123?at=0', '{"name": "foo"}', method=HTTPMethod.PUT,
                                                          headers=self._expected_headers())

    def test_send_request_should_return_empty_string_when_no_response_data(self):
        self.connection_mock.send.return_value = self._connection_response(None)

        resp = self.ftd_plugin.send_request('/test', HTTPMethod.GET)

        assert '' == resp
        self.connection_mock.send.assert_called_once_with('/test', None, method=HTTPMethod.GET,
                                                          headers=self._expected_headers())

    def test_send_request_should_resend_request_when_token_expires(self):
        self.connection_mock.send.side_effect = [
            self._connection_response('', 408),
            self._connection_response({'access_token': 'NEW_ACCESS_TOKEN', 'refresh_token': 'NEW_REFRESH_TOKEN'}),
            self._connection_response({'foo': 'bar'})
        ]

        resp = self.ftd_plugin.send_request('/test', HTTPMethod.GET)

        assert {'foo': 'bar'} == resp
        assert 'NEW_ACCESS_TOKEN' == self.ftd_plugin.access_token
        assert 'NEW_REFRESH_TOKEN' == self.ftd_plugin.refresh_token

    @patch('os.path.isdir', mock.Mock(return_value=False))
    def test_download_file(self):
        self.connection_mock.send.return_value = self._connection_response('File content')

        open_mock = mock_open()
        with patch('%s.open' % BUILTINS_NAME, open_mock):
            self.ftd_plugin.download_file('/files/1', '/tmp/test.txt')

        open_mock.assert_called_once_with('/tmp/test.txt', 'wb')
        open_mock().write.assert_called_once_with(b'File content')

    @patch('os.path.isdir', mock.Mock(return_value=True))
    def test_download_file_should_extract_filename_from_headers(self):
        self.connection_mock.send.return_value = self._connection_response('File content')
        filename = 'test_file.txt'
        self.connection_mock.send.return_value.info = lambda: {
            'Content-Disposition': 'attachment; filename="%s"' % filename
        }

        open_mock = mock_open()
        with patch('%s.open' % BUILTINS_NAME, open_mock):
            self.ftd_plugin.download_file('/files/1', '/tmp/')

        open_mock.assert_called_once_with('/tmp/%s' % filename, 'wb')
        open_mock().write.assert_called_once_with(b'File content')

    @patch('os.path.basename', mock.Mock(return_value='test.txt'))
    @patch('httpapi_plugins.ftd.encode_multipart_formdata',
           mock.Mock(return_value=('--Encoded data--', 'multipart/form-data')))
    def test_upload_file(self):
        self.connection_mock.send.return_value = self._connection_response({'id': '123'})

        open_mock = mock_open()
        with patch('%s.open' % BUILTINS_NAME, open_mock):
            resp = self.ftd_plugin.upload_file('/tmp/test.txt', '/files')

        assert {'id': '123'} == resp
        exp_headers = self._expected_headers()
        exp_headers['Content-Length'] = len('--Encoded data--')
        exp_headers['Content-Type'] = 'multipart/form-data'
        self.connection_mock.send.assert_called_once_with('/files', data='--Encoded data--',
                                                          headers=exp_headers, method=HTTPMethod.POST)
        open_mock.assert_called_once_with('/tmp/test.txt', 'rb')

    @patch.object(FdmSwaggerParser, 'parse_spec')
    def test_get_operation_spec(self, parse_spec_mock):
        self.connection_mock.send.return_value = self._connection_response(None)
        parse_spec_mock.return_value = {
            OPERATIONS: {'testOp': 'Specification for testOp'}
        }

        assert 'Specification for testOp' == self.ftd_plugin.get_operation_spec('testOp')
        assert self.ftd_plugin.get_operation_spec('nonExistingTestOp') is None

    @patch.object(FdmSwaggerParser, 'parse_spec')
    def test_get_model_spec(self, parse_spec_mock):
        self.connection_mock.send.return_value = self._connection_response(None)
        parse_spec_mock.return_value = {
            MODELS: {'TestModel': 'Specification for TestModel'}
        }

        assert 'Specification for TestModel' == self.ftd_plugin.get_model_spec('TestModel')
        assert self.ftd_plugin.get_model_spec('NonExistingTestModel') is None

    @staticmethod
    def _connection_response(response, status_code=200):
        response_str = json.dumps(response) if type(response) is dict else response
        response_mock = BytesIO(response_str.encode('utf-8') if response_str else None)
        if status_code == 200:
            return response_mock
        else:
            return HTTPError('http://testhost.com', status_code, '', {}, response_mock)

    def _expected_headers(self):
        return {
            'Accept': 'application/json',
            'Authorization': 'Bearer %s' % self.ftd_plugin.access_token,
            'Content-Type': 'application/json'
        }
