# Introduction to FTD Ansible

A collection of Ansible modules that automate configuration management and execution of operational tasks on
Cisco Firepower Threat Defense (FTD) devices.

The modules configure virtual and physical devices by sending HTTP(S) calls formatted according to the REST API
specification.

FTD Ansible modules are powerful and easy to use:

```yaml
- hosts: ftd_devices
  connection: httpapi
  tasks:
    - name: Create a network
      ftd_configuration:
          operation: "addNetworkObject"
          data:
             name: "any-ipv4"
             subType: "NETWORK"
             value: "0.0.0.0/0"
             type: "networkobject"
 ```
