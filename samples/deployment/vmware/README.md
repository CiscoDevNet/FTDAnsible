# Setup Guide

## Setup dependencies

1. Create virtual env
    ```bash
    virtualenv -p python3.7 ./venv
    source venv/bin/activate
    pip install ansible pyvmomi
    ```

1. Install vSphere Automation Python SDK
    ```bash
    git clone https://github.com/vmware/vsphere-automation-sdk-python.git
    cd vsphere-automation-sdk-python
    pip install --upgrade --force-reinstall -r requirements.txt --extra-index-url file://`pwd`/lib
    ```

1. Set correct values for the following demo_cloud.vmware.yaml:
    ```yaml
    plugin: "vmware_vm_inventory"
    hostname: "vmware.api.host.com"
    username: "username"
    password: "passwd"
    ```

1. Verify results
    ```bash
    ansible-inventory -i demo_cloud.vmware.yaml --list
    ```

## Prepare playbook
Update the following lines with correct values in the playbook deploy_and_destroy.yaml:
```yaml
  ...
  vars:
    vcenter_hostname: "vmware.api.host.com"
    vcenter_username: "username"
    vcenter_password: "username"
    vcenter_datacenter: "dc.name"
    vcenter_resource_pool: "some.resource.pool"
    vcenter_folder_name: "some.folder.name"
    mgmt_network_name: "some.network.name"
    new_vm_name: "Test_vFTD"
    new_passwd: "customPasswd"
  ...
  get_url:
    url: "https://some.file/server/Cisco_Firepower_Threat_Defense_Virtual-VI-6.4.0-1304.ovf"
  ...
  get_url:
     url: "https://some.file/server/Cisco_Firepower_Threat_Defense_Virtual-6.4.0-1304.vmdk"
```
## Run playbook
Run as: 
```bash
ansible-playbook -i demo_cloud.vmware.yaml deploy_and_destroy.yaml 
```

## Known issues
1. Slow Inventory load:
    - partially mitigated using ansible inventory cache plugins;
    - partially mitigated by execution of the playbook from the host which is closer to the cloud.

1. Deploy_ovf does not support OVF path as URL, only local file path for now:
    - The issue has been reported(https://github.com/ansible/ansible/issues/42666)  - development started.
    
## References
- https://docs.ansible.com/ansible/latest/plugins/inventory.html
- https://docs.ansible.com/ansible/latest/plugins/inventory/vmware_vm_inventory.html
