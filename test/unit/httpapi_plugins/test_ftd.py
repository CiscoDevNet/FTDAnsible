import json
import os
import unittest
from unittest import mock

from ansible.compat.tests.mock import mock_open, patch
from ansible.errors import AnsibleConnectionFailure
from ansible.module_utils.six import BytesIO, PY3
from ansible.module_utils.six.moves.urllib.error import HTTPError
from ansible.module_utils.connection import ConnectionError

from httpapi_plugins.ftd import HttpApi, API_TOKEN_PATH_ENV_VAR
from module_utils.fdm_swagger_client import SpecProp, FdmSwaggerParser
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

    def test_login_should_request_tokens_when_no_refresh_token(self):
        self.connection_mock.send.return_value = self._connection_response(
            {'access_token': 'ACCESS_TOKEN', 'refresh_token': 'REFRESH_TOKEN'}
        )

        self.ftd_plugin.login('foo', 'bar')

        assert 'ACCESS_TOKEN' == self.ftd_plugin.access_token
        assert 'REFRESH_TOKEN' == self.ftd_plugin.refresh_token
        expected_body = json.dumps({'grant_type': 'password', 'username': 'foo', 'password': 'bar'})
        self.connection_mock.send.assert_called_once_with(mock.ANY, expected_body, headers=mock.ANY, method=mock.ANY)

    def test_login_should_update_tokens_when_refresh_token_exists(self):
        self.ftd_plugin.refresh_token = 'REFRESH_TOKEN'
        self.connection_mock.send.return_value = self._connection_response(
            {'access_token': 'NEW_ACCESS_TOKEN', 'refresh_token': 'NEW_REFRESH_TOKEN'}
        )

        self.ftd_plugin.login('foo', 'bar')

        assert 'NEW_ACCESS_TOKEN' == self.ftd_plugin.access_token
        assert 'NEW_REFRESH_TOKEN' == self.ftd_plugin.refresh_token
        expected_body = json.dumps({'grant_type': 'refresh_token', 'refresh_token': 'REFRESH_TOKEN'})
        self.connection_mock.send.assert_called_once_with(mock.ANY, expected_body, headers=mock.ANY, method=mock.ANY)

    @patch.dict(os.environ, {API_TOKEN_PATH_ENV_VAR: '/testLoginUrl'})
    def test_login_should_use_env_variable_when_set(self):
        self.connection_mock.send.return_value = self._connection_response(
            {'access_token': 'ACCESS_TOKEN', 'refresh_token': 'REFRESH_TOKEN'}
        )

        self.ftd_plugin.login('foo', 'bar')

        self.connection_mock.send.assert_called_once_with('/testLoginUrl', mock.ANY, headers=mock.ANY, method=mock.ANY)

    def test_login_raises_exception_when_no_refresh_token_and_no_credentials(self):
        with self.assertRaises(AnsibleConnectionFailure) as res:
            self.ftd_plugin.login(None, None)
        assert 'Username and password are required' in str(res.exception)

    def test_login_raises_exception_when_invalid_response(self):
        self.connection_mock.send.return_value = self._connection_response(
            {'no_access_token': 'ACCESS_TOKEN'}
        )

        with self.assertRaises(ConnectionError) as res:
            self.ftd_plugin.login('foo', 'bar')

        assert 'Invalid JSON response during connection authentication' in str(res.exception)

    def test_logout_should_revoke_tokens(self):
        self.ftd_plugin.access_token = 'ACCESS_TOKEN_TO_REVOKE'
        self.ftd_plugin.refresh_token = 'REFRESH_TOKEN_TO_REVOKE'
        self.connection_mock.send.return_value = self._connection_response(None)

        self.ftd_plugin.logout()

        assert self.ftd_plugin.access_token is None
        assert self.ftd_plugin.refresh_token is None
        expected_body = json.dumps({'grant_type': 'revoke_token', 'access_token': 'ACCESS_TOKEN_TO_REVOKE',
                                    'token_to_revoke': 'REFRESH_TOKEN_TO_REVOKE'})
        self.connection_mock.send.assert_called_once_with(mock.ANY, expected_body, headers=mock.ANY, method=mock.ANY)

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

    def test_send_request_raises_exception_when_invalid_response(self):
        self.connection_mock.send.return_value = self._connection_response('nonValidJson')

        with self.assertRaises(ConnectionError) as res:
            self.ftd_plugin.send_request('/test', HTTPMethod.GET)

        assert 'Invalid JSON response' in str(res.exception)

    def test_handle_httperror_should_update_tokens_and_retry_on_auth_errors(self):
        self.ftd_plugin.refresh_token = 'REFRESH_TOKEN'
        self.connection_mock.send.return_value = self._connection_response(
            {'access_token': 'NEW_ACCESS_TOKEN', 'refresh_token': 'NEW_REFRESH_TOKEN'}
        )

        retry = self.ftd_plugin.handle_httperror(HTTPError('http://testhost.com', 401, '', {}, None))

        assert retry
        assert 'NEW_ACCESS_TOKEN' == self.ftd_plugin.access_token
        assert 'NEW_REFRESH_TOKEN' == self.ftd_plugin.refresh_token

    def test_handle_httperror_should_not_retry_on_non_auth_errors(self):
        assert not self.ftd_plugin.handle_httperror(HTTPError('http://testhost.com', 500, '', {}, None))

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
        filename = 'test_file.txt'
        response = mock.Mock()
        response.info.return_value = {'Content-Disposition': 'attachment; filename="%s"' % filename}
        _, response_data = self._connection_response('File content')
        self.connection_mock.send.return_value = response, response_data

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

    @patch('os.path.basename', mock.Mock(return_value='test.txt'))
    @patch('httpapi_plugins.ftd.encode_multipart_formdata',
           mock.Mock(return_value=('--Encoded data--', 'multipart/form-data')))
    def test_upload_file_raises_exception_when_invalid_response(self):
        self.connection_mock.send.return_value = self._connection_response('invalidJsonResponse')

        open_mock = mock_open()
        with patch('%s.open' % BUILTINS_NAME, open_mock):
            with self.assertRaises(ConnectionError) as res:
                self.ftd_plugin.upload_file('/tmp/test.txt', '/files')

        assert 'Invalid JSON response after uploading the file' in str(res.exception)

    @patch.object(FdmSwaggerParser, 'parse_spec')
    def test_get_operation_spec(self, parse_spec_mock):
        self.connection_mock.send.return_value = self._connection_response(None)
        parse_spec_mock.return_value = {
            SpecProp.OPERATIONS: {'testOp': 'Specification for testOp'}
        }

        assert 'Specification for testOp' == self.ftd_plugin.get_operation_spec('testOp')
        assert self.ftd_plugin.get_operation_spec('nonExistingTestOp') is None

    @patch.object(FdmSwaggerParser, 'parse_spec')
    def test_get_model_spec(self, parse_spec_mock):
        self.connection_mock.send.return_value = self._connection_response(None)
        parse_spec_mock.return_value = {
            SpecProp.MODELS: {'TestModel': 'Specification for TestModel'}
        }

        assert 'Specification for TestModel' == self.ftd_plugin.get_model_spec('TestModel')
        assert self.ftd_plugin.get_model_spec('NonExistingTestModel') is None

    @staticmethod
    def _connection_response(response):
        response_str = json.dumps(response) if type(response) is dict else response
        response_mock = BytesIO(response_str.encode('utf-8') if response_str else None)
        return None, response_mock

    def _expected_headers(self):
        return {
            'Accept': 'application/json',
            'Authorization': 'Bearer %s' % self.ftd_plugin.access_token,
            'Content-Type': 'application/json'
        }
