# Getting Started

This section gives a good introduction how to get started with FTD Ansible modules. 

First, make sure that Ansible with FTD modules is [installed](./installation_guide.md).

## Managing configuration with Ansible

Configuring FTD devices is simple with the help of [`ftd_configuration`](https://docs.ansible.com/ansible/latest/modules/ftd_configuration_module.html)
module. The module exposes all operations available in REST API in a form of Ansible tasks.

Begin by finding a necessary operation from [Operation Index](operations/index.md). Most operations correspond to CRUD 
functions managing [configuration models](models/index.md) (e.g., `addNetworkObject` creates `NetworkObject` instances).

Wrap the selected operation in a playbook task. Each `ftd_configuration` task must contain an `operation` parameter 
corresponding to the operation name. For example, a playbook with `addNetworkObject` task might look like this:

```yaml
- hosts: all
  connection: httpapi
  tasks:
    - name: Create localhost network
      ftd_configuration:
        operation: addNetworkObject
        data:
          name: LocalhostNetwork
          subType: HOST
          value: 127.0.0.1
          type: networkobject
```

More examples can be found [here](./examples.md).

## Registering objects as Ansible facts

## Understanding playbook's idempotency
