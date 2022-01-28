# Setup Guide

## Setup dependencies
1. Create Python virtual environment
    ```bash
    python -m venv ./venv
    source venv/bin/activate
    pip install ansible
    ```

## Setup KVM host
1. Set environment-specific variables in the _inventory.yaml_
1. Run a playbook
    ```bash
    ansible-playbook -i inventory.yaml setup_host.yaml
    ```

## Deploy a new vFTD
1. Run a playbook
    ```bash
    ansible-playbook -i inventory.yaml deploy_vm.yaml
    ```

## References
- https://docs.ansible.com/ansible/latest/modules/virt_module.html
- https://docs.ansible.com/ansible/latest/modules/virt_net_module.html

