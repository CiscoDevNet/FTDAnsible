#!/usr/bin/python

# Copyright (c) 2019 Cisco and/or its affiliates.
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#

from __future__ import absolute_import, division, print_function

__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'network'}

DOCUMENTATION = """
---
module: ftd_install
short_description: Configure FTD devices
version_added: "2.8"
author: "Cisco Systems, Inc."
options:
  ip:
    description:
      - Device IP Address to access TFTP Server
    required: true
  netmask:
    description:
      - Device Netmask
    required: true
  gateway:
    description:
      - Device Gateway
    required: true
  hostname:
    description:
      - Hostname to be set
  password:
    description:
      - Password to login   
  ssh_port:
    description:
      - Port of device on terminal server   
    required: true 
  tftp_server:
    description:
      - TFTP Server IP Address
    required: true
  dns_server:
    description:
      - DNS server
    required: true
  rommon_file:
    description:
      - Boot image to be transferred via TFTP
    required: true
  ftd_file:
    description:
      - FTD image to be transferred via HTTP
    required: true
"""

EXAMPLES = """
  - name: Install image v6.2.3 on FTD
    ftd_install:
      device_hostname: firepower
      device_password: Sourcefire
      device_ip: 192.168.0.1
      device_netmask: 255.255.255.0
      device_gateway: 192.168.0.254
      dns_server: 8.8.8.8

      console_ip: 10.89.0.0
      console_port: 2004
      console_username: console_user
      console_password: console_pass

      image_site: ast
      image_branch: Release
      image_version: 6.2.3-83
"""

from ansible.module_utils.basic import AnsibleModule
from kick.device2.ftd5500x.actions.ftd5500x import Ftd5500x
from ansible.module_utils.connection import Connection

try:
    from ansible.module_utils.configuration import BaseConfigurationResource, ParamName, PATH_PARAMS_FOR_DEFAULT_OBJ
except ImportError:
    from module_utils.configuration import BaseConfigurationResource, ParamName, PATH_PARAMS_FOR_DEFAULT_OBJ

GET_SYSTEM_INFO_OPERATION = 'getSystemInformation'


def main():
    fields = dict(
        device_hostname=dict(type='str', required=True),
        device_password=dict(type='str', required=True),
        device_ip=dict(type='str', required=True),
        device_netmask=dict(type='str', required=True),
        device_gateway=dict(type='str', required=True),
        dns_server=dict(type='str', required=True),

        console_ip=dict(type='str', required=True),
        console_port=dict(type='str', required=True),
        console_username=dict(type='str', required=True),
        console_password=dict(type='str', required=True),

        image_site=dict(type='str', required=True),
        image_branch=dict(type='str', required=True),
        image_version=dict(type='str', required=True)
    )
    module = AnsibleModule(argument_spec=fields)

    hostname, password = module.params["device_hostname"], module.params["device_password"]
    console_ip, console_port = module.params["console_ip"], module.params["console_port"]
    console_username, console_password = module.params["console_username"], module.params["console_password"]
    device_ip, device_netmask, device_gateway = \
        module.params["device_ip"], module.params["device_netmask"], module.params["device_gateway"]
    dns_server = module.params["dns_server"]
    img_site, img_branch, img_version = module.params["image_site"], module.params["image_branch"], module.params["image_version"]

    connection = Connection(module._socket_path)
    resource = BaseConfigurationResource(connection, module.check_mode)

    current_ftd_version = get_current_ftd_version(resource)
    if img_version == current_ftd_version:
        return module.exit_json(changed=False, msg="FTD already has %s version of software installed." % img_version)

    ftd = Ftd5500x(hostname=hostname,
                   login_password=password,
                   sudo_password=password)
    dev = None

    try:
        dev = ftd.ssh_console(ip=console_ip,
                              port=console_port,
                              username=console_username,
                              password=console_password)

        dev.baseline_by_branch_and_version(site=img_site,
                                           branch=img_branch,
                                           version=img_version,
                                           uut_ip=device_ip,
                                           uut_netmask=device_netmask,
                                           uut_gateway=device_gateway,
                                           dns_server=dns_server,
                                           hostname=hostname)

        module.exit_json(changed=True)
    finally:
        dev.disconnect()


def get_current_ftd_version(resource):
    path_params = {ParamName.PATH_PARAMS: PATH_PARAMS_FOR_DEFAULT_OBJ}
    system_info = resource.execute_operation(GET_SYSTEM_INFO_OPERATION, path_params)
    ftd_version = system_info['softwareVersion']
    return ftd_version


if __name__ == '__main__':
    main()
