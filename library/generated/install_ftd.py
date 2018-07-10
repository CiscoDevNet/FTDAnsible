#!/usr/bin/python

# Copyright (c) 2018 Cisco Systems, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'network'}



from ansible.module_utils.basic import AnsibleModule
from kick.device2.ftd5500x.actions.ftd5500x import Ftd5500x


def main():

    fields = dict(
        UUT_IP=dict(type='str', required=True),
        UUT_NETMASK=dict(type='str', required=True),
        UUT_GATEWAY=dict(type='str', required=True),
        UUT_HOSTNAME=dict(type='str'),
        UUT_USERNAME=dict(type='str'),
        UUT_PASSWORD=dict(type='str'),
        CONSOLE_PORT=dict(type='str', required=True),
        TFTP_SERVER_IP=dict(type='str', required=True),
        DNS_SERVERS=dict(type='str', required=True),
        ROMMON_FILE=dict(type='str', required=True),
        FTD_FILE=dict(type='str', required=True)
    )

    module = AnsibleModule(argument_spec=fields)

    ip = module.params["UUT_IP"]
    netmask = module.params["UUT_NETMASK"]
    gateway = module.params["UUT_GATEWAY"]
    hostname = module.params["UUT_HOSTNAME"]
    username = module.params["UUT_USERNAME"]
    password = module.params["UUT_PASSWORD"]
    port = module.params["CONSOLE_PORT"]
    tftpServerIp = module.params["TFTP_SERVER_IP"]
    dnsServers = module.params["DNS_SERVERS"]
    rommonFile = module.params["ROMMON_FILE"]
    ftdFile = module.params["FTD_FILE"]

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
                            is_device_kenton=True,
                            power_cycle_flag=False
                            )

    dev.disconnect()


if __name__ == '__main__':
    main()
