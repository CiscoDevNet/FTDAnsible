# Installation Guide

Welcome to the FTD Ansible Installation Guide!

## Dependency Requirements

FTD modules can be run from any machine with Ansible 2.9 or higher installed.

Ansible itself requires Python 2 (version 2.7) or Python 3 (versions 3.5 and higher) installed. 

## Installing Ansible with FTD modules

### Using Ansible
Ansible (version 2.9 and higher) automatically [contains](https://docs.ansible.com/ansible/latest/modules/list_of_all_modules.html?highlight=ftd) 
FTD modules inside, and in most cases installing the latest Ansible should be sufficient to run the playbooks. We periodically update FTD modules
and they get released in Ansible according to the [roadmap](https://docs.ansible.com/ansible/latest/roadmap/index.html).

To run the playbooks:

1. Follow [Ansible Installation Guide](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html)
to install the latest version;
1. [Create](#creating-inventory) an inventory file for FTD devices;
1. Run the playbook:
```
ansible-playbook test_playbook.yml
``` 

### Using Docker Image

If you want to benefit from the most recent updates and bug fixes and do not want to be dependent on [Ansible Roadmap](https://docs.ansible.com/ansible/latest/roadmap/index.html), 
you can pull our Docker Image with the latest FTD modules and run the playbooks inside a Docker container. 

1. Pull the latest version of `ftd-ansible` image from Docker Hub:
```
docker pull ciscodevnet/ftd-ansible
```

1. [Create](#creating-inventory) an inventory file for FTD devices;

1. Run the playbook in Docker mounting playbook folder to `/ftd-ansible/playbooks` and inventory file to `/etc/ansible/hosts`:
```
docker run -v $(pwd)/samples:/ftd-ansible/playbooks -v $(pwd)/inventory/sample_hosts:/etc/ansible/hosts ciscodevnet/ftd-ansible playbooks/test_playbook.yml
```

### Using source code

Not only do you need to have the most recent updates, but also feel eager to experiment with the source code? Then, 
follow the development setup and clone out [Git repository](https://github.com/CiscoDevNet/FTDAnsible).  

1. Clone the FTDAnsible repository:
```
git clone https://github.com/CiscoDevNet/FTDAnsible.git
```

1. Make sure that Python version [supported by Ansible](#dependency-requirements) is installed, and create 
a virtual environment:
```
cd FTDAnsible
python -m venv venv
. venv/bin/activate
```

1. Install dependencies and update Python path to include the project's directory:
```
pip install -r requirements.txt
export PYTHONPATH=.:$PYTHONPATH
```

1. [Create](#creating-inventory) an inventory file for FTD devices;
   
1. Run the playbook:
``` 
ansible-playbook test_playbook.yml
```

## Creating Inventory

[Ansible inventory](https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html) contains information
about systems where the playbooks should be run. You should create an inventory file with information about FTD
devices you would like to configure. The default location for inventory is `/etc/ansible/hosts`, but you can specify a
different path by adding the `-i <path>` argument to the `ansible-playbook` command.

Here is an example of the inventory file with one local FTD device:

```
[ftd]
my-ftd ansible_host=192.168.1.1 ansible_httpapi_port=443 ansible_network_os=ftd ansible_user=admin ansible_password=123qwe ansible_httpapi_use_ssl=True
```

FTD modules __require__ the following host parameters in the inventory file:
 
* `ansible_host` - a hostname or an IP address of the FTD device;
* `ansible_network_os` - an OS of the networking device, must be set to `ftd` when using FTD modules;
* `ansible_user` - a username for the FTD device;
* `ansible_password` - a password for the given username;

Additionally, these __optional__ parameters can be used:

* `ansible_httpapi_port` - an HTTP port that the FTD device listens to (default is `443` for HTTPS and `80` for HTTP);
* `ansible_httpapi_use_ssl` - `True` to connect using HTTPS or `False` to connect via HTTP (default is `False`);
* `ansible_httpapi_ftd_token_path` - a URL for the token endpoint on the FTD device (default URL is `/api/fdm/v2/fdm/token`);
* `ansible_httpapi_ftd_spec_path` - a URL for the Swagger specification on the FTD device (default URL is `/apispec/ngfw.json`);
* `ansible_httpapi_validate_certs` - an option specifying whether to validate SSL certificates or not.

### Using Vault

To keep sensitive data (e.g., `ansible_password`) in encrypted files, rather than as plaintext in inventory files, use
[Ansible Vault](https://docs.ansible.com/ansible/latest/user_guide/vault.html) feature.

Vault can encrypt any file used by Ansible including `group_vars/` or `host_vars/` variables, variables 
loaded by `include_vars` or `vars_files`, and variable files passed as `-e @file` argument to `ansible-playbook` command.

To create an encrypted vault file, run the following command:
```
ansible-vault create secret
```
First, you will be prompted for a password, then the editor will be launched and once you are done, the encrypted file
is created. To use the encrypted file in Ansible, add the `--ask-vault-pass` 
to any `ansible` or `ansible-playbook` command:
```
ansible-playbook test_playbook.yml --ask-vault-pass -e @secret
```

More information about Vault can be found in Ansible Documentation:
 * [Ansible Vault](https://docs.ansible.com/ansible/latest/user_guide/vault.html)
 * [Using Vault in playbooks](https://docs.ansible.com/ansible/latest/user_guide/playbooks_vault.html) 
