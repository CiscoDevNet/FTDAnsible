# Setup Guide

## Setup dependencies
1. Create python virtual env
    ```bash
    virtualenv -p python3.6 ./venv
    source venv/bin/activate
    pip install ansible
    ```

## Setup KVM host

1. Set environment specific variables in the _inventory.yaml_
1. Run playbook to setup kvm hosts
    ```bash
    ansible-playbook -i inventory.yaml setup_host.yaml
    ```

## Deploy new vFTD
1. Run playbook
    ```bash
    ansible-playbook -i inventory.yaml deploy_vm.yaml
    ```

## Useful Links
- https://docs.ansible.com/ansible/latest/modules/virt_module.html
- https://docs.ansible.com/ansible/latest/modules/virt_net_module.html

