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
    tftp_server="10.0.0.1",
    rommon_file_location="boot/ftd-boot-1.9.2.0.lfbff",
    image_file_location="http://10.0.0.1/Release/ftd-6.2.3-83.pkg"
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

    @pytest.fixture(autouse=True)
    def ftd_5500x_mock(self, mocker):
        return mocker.patch('library.ftd_install.Ftd5500x')

    def test_module_should_fail_when_platform_is_not_supported(self, config_resource_mock):
        config_resource_mock.execute_operation.return_value = {'platformModel': 'nonSupportedPlatform'}

        set_module_args(dict(DEFAULT_INSTALL_PARAMS))
        with pytest.raises(AnsibleFailJson) as ex:
            self.module.main()

        result = ex.value.args[0]
        assert result['failed']
        assert result['msg'] == "Platform 'nonSupportedPlatform' is not supported by this module."

    def test_module_should_return_when_software_is_already_installed(self, config_resource_mock):
        config_resource_mock.execute_operation.return_value = {
            'softwareVersion': '6.3.0-11',
            'platformModel': 'Cisco ASA5516-X Threat Defense'
        }
        module_params = dict(DEFAULT_INSTALL_PARAMS)
        module_params['image_version'] = '6.3.0-11'

        set_module_args(module_params)
        with pytest.raises(AnsibleExitJson) as ex:
            self.module.main()

        result = ex.value.args[0]
        assert not result['changed']
        assert result['msg'] == 'FTD already has 6.3.0-11 version of software installed.'

    def test_module_should_fill_management_ip_values_when_missing(self, config_resource_mock, ftd_5500x_mock):
        config_resource_mock.execute_operation.side_effect = [
            {
                'softwareVersion': '6.3.0-11',
                'platformModel': 'Cisco ASA5516-X Threat Defense'
            },
            {
                'items': [{
                    'ipv4Address': '192.168.1.1',
                    'ipv4NetMask': '255.255.255.0',
                    'ipv4Gateway': '192.168.0.1'
                }]
            }
        ]
        module_params = dict(DEFAULT_INSTALL_PARAMS)
        del module_params['device_ip']
        del module_params['device_netmask']
        del module_params['device_gateway']

        set_module_args(module_params)
        with pytest.raises(AnsibleExitJson):
            self.module.main()

        console_mock = ftd_5500x_mock.return_value.ssh_console
        console_mock.assert_called_once_with(
            ip=module_params['console_ip'],
            password=module_params['console_password'],
            port=module_params['console_port'],
            username=module_params['console_username']
        )
        console_mock.return_value.rommon_to_new_image.assert_called_once_with(
            rommon_tftp_server=module_params['tftp_server'],
            rommon_image=module_params['rommon_file_location'],
            pkg_image=module_params['image_file_location'],
            uut_ip='192.168.1.1',
            uut_netmask='255.255.255.0',
            uut_gateway='192.168.0.1',
            dns_server=module_params['dns_server'],
            hostname=module_params['device_hostname']
        )

    def test_module_should_fill_dns_server_when_missing(self, config_resource_mock, ftd_5500x_mock):
        config_resource_mock.execute_operation.side_effect = [
            {
                'softwareVersion': '6.3.0-11',
                'platformModel': 'Cisco ASA5516-X Threat Defense'
            },
            {
                'items': [{
                    'dnsServerGroup': {
                        'id': '123'
                    }
                }]
            },
            {
                'dnsServers': [{
                    'ipAddress': '8.8.9.9'
                }]
            }
        ]
        module_params = dict(DEFAULT_INSTALL_PARAMS)
        del module_params['dns_server']

        set_module_args(module_params)
        with pytest.raises(AnsibleExitJson):
            self.module.main()

        console_mock = ftd_5500x_mock.return_value.ssh_console
        console_mock.assert_called_once_with(
            ip=module_params['console_ip'],
            password=module_params['console_password'],
            port=module_params['console_port'],
            username=module_params['console_username']
        )
        console_mock.return_value.rommon_to_new_image.assert_called_once_with(
            rommon_tftp_server=module_params['tftp_server'],
            rommon_image=module_params['rommon_file_location'],
            pkg_image=module_params['image_file_location'],
            uut_ip=module_params['device_ip'],
            uut_netmask=module_params['device_netmask'],
            uut_gateway=module_params['device_gateway'],
            dns_server='8.8.9.9',
            hostname=module_params['device_hostname']
        )
