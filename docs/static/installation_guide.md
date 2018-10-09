# Installation Guide

Welcome to the FTD Ansible Installation Guide!

## Dependency Requirements

FTD modules can be run from any machine with Ansible 2.7 or higher installed.

Ansible itself requires Python 2 (version 2.7) or Python 3 (versions 3.5 and higher) installed. 

## Installing Ansible with FTD modules

### Using Ansible
Ansible (version 2.7 and higher) automatically [contains](https://docs.ansible.com/ansible/latest/modules/list_of_all_modules.html?highlight=ftd) 
FTD modules inside, and in most cases installing the latest Ansible should be sufficient to run the playbooks. We periodically update FTD modules
and they get released in Ansible according to the [roadmap](https://docs.ansible.com/ansible/latest/roadmap/index.html).

To run the playbooks:

1. Follow [Ansible Installation Guide](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html)
to install the latest version;
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

1. Run the playbook in Docker mounting playbook folder to `/ftd-ansible/playbooks` and inventory file to `/etc/ansible/hosts`:
```
docker run -v $(pwd)/samples:/ftd-ansible/playbooks -v $(pwd)/inventory/sample_hosts:/etc/ansible/hosts ciscodevnet/ftd-ansible test_playbook.yml
```
