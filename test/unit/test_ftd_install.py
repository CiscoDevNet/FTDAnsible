from __future__ import absolute_import

import pytest
from ansible.module_utils import basic
from units.modules.utils import set_module_args, exit_json, fail_json, AnsibleFailJson, AnsibleExitJson

from library import ftd_install

DEFAULT_INSTALL_PARAMS = dict(
    device_hostname="firepower",
    device_password="pass",
    device_ip="192.168.0.1",
    device_netmask="255.255.255.0",
    device_gateway="192.168.0.254",
    dns_server="8.8.8.8",
    console_ip="10.89.0.0",
    console_port="2004",
    console_username="console_user",
    console_password="console_pass",
    image_site="ast",
    image_branch="Release",
    image_version="6.2.3-83"
)


class TestFtdInstall(object):
    module = ftd_install

    @pytest.fixture(autouse=True)
    def module_mock(self, mocker):
        return mocker.patch.multiple(basic.AnsibleModule, exit_json=exit_json, fail_json=fail_json)

    @pytest.fixture(autouse=True)
    def connection_mock(self, mocker):
        connection_class_mock = mocker.patch('library.ftd_install.Connection')
        return connection_class_mock.return_value

    @pytest.fixture
    def config_resource_mock(self, mocker):
        resource_class_mock = mocker.patch('library.ftd_install.BaseConfigurationResource')
        return resource_class_mock.return_value

    def test_module_should_return_when_software_is_already_installed(self, config_resource_mock):
        config_resource_mock.execute_operation.return_value = {'softwareVersion': '6.3.0-11'}
        module_params = dict(DEFAULT_INSTALL_PARAMS)
        module_params['image_version'] = '6.3.0-11'

        set_module_args(module_params)
        with pytest.raises(AnsibleExitJson) as ex:
            self.module.main()

        result = ex.value.args[0]
        assert not result['changed']
        assert result['msg'] == 'FTD already has 6.3.0-11 version of software installed.'
