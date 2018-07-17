#!/usr/bin/python

# Copyright (c) 2018 Cisco Systems, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'network'}

DOCUMENTATION = """
---
module: install_ftd
short_description: Configure FTD devices
version_added: "2.7"
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
  console_port:
    description:
      - Port of device on terminal server   
    required: true 
  tftp_server_ip:
    description:
      - TFTP Server IP Address
    required: true
  dns_servers:
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
- name: install ftd
  install_ftd:
    ip: '192.168.0.156'
    netmask: '255.255.255.0'
    gateway: '192.168.0.254'
    hostname: 'firepower'
    password: 'Admin123'
    console_port: '2004'
    tftp_server_ip: '10.88.90.130'
    dns_servers: '171.70.168.183'
    rommon_file: 'xyz/ftd-boot.cdisk'
    ftd_file: 'http://10.88.90.130/xyz/ftd-6.3.0-xxx.pkg'
"""

from ansible.module_utils.basic import AnsibleModule
from kick.device2.ftd5500x.actions.ftd5500x import Ftd5500x


def main():

    fields = dict(
        ip=dict(type='str', required=True),
        netmask=dict(type='str', required=True),
        gateway=dict(type='str', required=True),
        hostname=dict(type='str'),
        password=dict(type='str'),
        console_port=dict(type='int', required=True),
        tftp_server_ip=dict(type='str', required=True),
        dns_servers=dict(type='str', required=True),
        rommon_file=dict(type='str', required=True),
        ftd_file=dict(type='path', required=True)
    )

    module = AnsibleModule(argument_spec=fields)

    ip = module.params["ip"]
    netmask = module.params["netmask"]
    gateway = module.params["gateway"]
    hostname = module.params["hostname"]
    password = module.params["password"]
    port = module.params["console_port"]
    tftpServerIp = module.params["tftp_server_ip"]
    dnsServers = module.params["dns_servers"]
    rommonFile = module.params["rommon_file"]
    ftdFile = module.params["ftd_file"]

    ftd = Ftd5500x(hostname=hostname, login_password=password, sudo_password=password)

    dev = ftd.ssh_console(ip=ip, port=port)

    dev.rommon_to_new_image(rommon_tftp_server=tftpServerIp,
                            pkg_image=ftdFile,
                            rommon_image=rommonFile,
                            uut_ip=ip,
                            uut_netmask=netmask,
                            uut_gateway=gateway,
                            dns_server=dnsServers,
                            hostname=hostname,
                            power_cycle_flag=False
                            )

    dev.disconnect()


if __name__ == '__main__':
    main()
