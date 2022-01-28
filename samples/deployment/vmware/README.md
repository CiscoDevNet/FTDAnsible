# Setup Guide

## Setup dependencies

1. Create Python virtual environment
    ```bash
    python -m venv ./venv
    source venv/bin/activate
    pip install ansible pyvmomi
    ```

1. Install vSphere Automation Python SDK
    ```bash
    git clone https://github.com/vmware/vsphere-automation-sdk-python.git
    cd vsphere-automation-sdk-python
    pip install --upgrade --force-reinstall -r requirements.txt --extra-index-url file://`pwd`/lib
    ```

1. Set environment variables:
    ```bash
    export VMWARE_SERVER=...vCenter hostname...
    export VMWARE_USERNAME=...vCenter username...
    export VMWARE_PASSWORD=...vCenter password...
    ```

1. Verify results
    ```bash
    ansible-inventory -i demo_cloud.vmware.yaml --list
    ```

## Set configuration options in the variables file
Replace placeholder values in the `vars.yaml` file 

## Run the playbook
Run as: 
```bash
ansible-playbook -i demo_cloud.vmware.yaml deploy_and_destroy.yaml 
```

## Known issues
1. Slow Inventory load:
    - partially mitigated using ansible inventory cache plugins;
    - partially mitigated by execution of the playbook from the host which is closer to the cloud.

1. Deploy_ovf does not support OVF path as URL, only local file path for now:
    - The [issue](https://github.com/ansible/ansible/issues/42666) has been reported on Github - development started.
    
## References
- https://docs.ansible.com/ansible/latest/plugins/inventory.html
- https://docs.ansible.com/ansible/latest/plugins/inventory/vmware_vm_inventory.html
