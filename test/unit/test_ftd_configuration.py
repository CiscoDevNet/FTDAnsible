from __future__ import absolute_import

import pytest
from ansible.module_utils import basic
from units.modules.utils import set_module_args, exit_json, fail_json, AnsibleFailJson, AnsibleExitJson

from library import ftd_configuration

try:
    from ansible.module_utils.common import FtdConfigurationError, FtdServerError, FtdUnexpectedResponse
    from ansible.module_utils.configuration import FtdInvalidOperationNameError, CheckModeException
    from ansible.module_utils.fdm_swagger_client import ValidationError
except ImportError:
    from module_utils.common import FtdConfigurationError, FtdServerError, FtdUnexpectedResponse
    from module_utils.configuration import FtdInvalidOperationNameError, CheckModeException
    from module_utils.fdm_swagger_client import ValidationError


class TestFtdConfiguration(object):
    module = ftd_configuration

    @pytest.fixture(autouse=True)
    def module_mock(self, mocker):
        return mocker.patch.multiple(basic.AnsibleModule, exit_json=exit_json, fail_json=fail_json)

    @pytest.fixture(autouse=True)
    def connection_mock(self, mocker):
        connection_class_mock = mocker.patch('library.ftd_configuration.Connection')
        return connection_class_mock.return_value

    @pytest.fixture
    def resource_mock(self, mocker):
        resource_class_mock = mocker.patch('library.ftd_configuration.BaseConfigurationResource')
        resource_instance = resource_class_mock.return_value
        return resource_instance.execute_operation

    def test_module_should_fail_when_ftd_invalid_operation_name_error(self, resource_mock):
        operation_name = 'test name'
        resource_mock.side_effect = FtdInvalidOperationNameError(operation_name)

        result = self._run_module_with_fail_json({'operation': operation_name})
        assert result['failed']
        assert 'Invalid operation name provided: %s' % operation_name == result['msg']

    def test_module_should_fail_when_ftd_configuration_error(self, resource_mock):
        operation_name = 'test name'
        msg = 'Foo error.'
        resource_mock.side_effect = FtdConfigurationError(msg)

        result = self._run_module_with_fail_json({'operation': operation_name})
        assert result['failed']
        assert 'Failed to execute %s operation because of the configuration error: %s' % (operation_name, msg) == \
               result['msg']

    def test_module_should_fail_when_ftd_server_error(self, resource_mock):
        operation_name = 'test name'
        code = 500
        response = {'error': 'foo'}
        resource_mock.side_effect = FtdServerError(response, code)

        result = self._run_module_with_fail_json({'operation': operation_name})
        assert result['failed']
        assert 'Server returned an error trying to execute %s operation. Status code: %s. ' \
               'Server response: %s' % (operation_name, code, response) == \
               result['msg']

    def test_module_should_fail_when_validation_error(self, resource_mock):
        operation_name = 'test name'
        msg = 'Foo error.'
        resource_mock.side_effect = ValidationError(msg)

        result = self._run_module_with_fail_json({'operation': operation_name})
        assert result['failed']
        assert msg == result['msg']

    def test_module_should_fail_when_unexpected_server_response(self, resource_mock):
        operation_name = 'test name'
        msg = 'Foo error.'
        resource_mock.side_effect = FtdUnexpectedResponse(msg)

        result = self._run_module_with_fail_json({'operation': operation_name})

        assert result['failed']
        assert msg == result['msg']

    def test_module_should_fail_when_check_mode_exception(self, resource_mock):
        operation_name = 'test name'
        msg = 'Foo error.'
        resource_mock.side_effect = CheckModeException(msg)

        result = self._run_module({'operation': operation_name})
        assert not result['changed']

    def test_module_should_run_successful(self, resource_mock):
        operation_name = 'test name'
        resource_mock.return_value = {'result': 'ok'}

        result = self._run_module({'operation': operation_name})
        assert result['response'] == {'result': 'ok'}

    def _run_module(self, module_args):
        set_module_args(module_args)
        with pytest.raises(AnsibleExitJson) as ex:
            self.module.main()
        return ex.value.args[0]

    def _run_module_with_fail_json(self, module_args):
        set_module_args(module_args)
        with pytest.raises(AnsibleFailJson) as exc:
            self.module.main()
        result = exc.value.args[0]
        return result
