# Getting Started

This section gives a good introduction how to get started with FTD Ansible modules. 

First, make sure that Ansible with FTD modules is [installed](./installation_guide.md).

## Managing configuration with Ansible

Configuring FTD devices is simple with the help of [`ftd_configuration`](https://docs.ansible.com/ansible/latest/modules/ftd_configuration_module.html)
module. The module exposes all operations available in REST API in a form of Ansible tasks.

Begin by finding a necessary operation from [Operation Index](operations/index.md). Most operations correspond to CRUD 
functions managing [configuration models](models/index.md) (e.g., `addNetworkObject` creates `NetworkObject` instances).

Wrap the selected operation in a playbook task. Each `ftd_configuration` task must contain an `operation` parameter 
corresponding to the operation name. In addition, the task might also have `data`, `path_params` and `query_params`
parameters that match body, URL parameters and query string in HTTP request accordingly.

For example, a playbook with a task for `addNetworkObject` operation might look like this:

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
          type: LocalhostNetwork
```

More examples can be found [here](./examples.md).

## Registering objects as Ansible facts

In order to reuse objects in subsequent plays during an ansible-playbook run, they should be registered as variables. 
FTD modules automatically register server responses as Ansible facts. Then, these facts can be used in the playbook as 
regular variables.

By default, fact names are constructed as `{OBJECT_TYPE}_{LOWERCASE_OBJECT_NAME}`. For example, an `addNetworkObject` 
play creating a `NetworkObject` named `LocalhostNetwork` registers the newly created object in a 
`networkobject_localhostnetwork` fact:

```
$ ansible-playbook test.yml -vvv

TASK [Create localhost network] ***********************************************************
ok: [localhost] => {
    "ansible_facts": {
        "networkobject_localhostnetwork": {
            "description": null,
            "dnsResolution": null,
            "id": "a016b91b-cbdb-11e8-8efc-8f046e5a37e0",
            "isSystemDefined": false,
            "links": {
                "self": "https://localhost/api/fdm/v2/object/networks/a016b91b-cbdb-11e8-8efc-8f046e5a37e0"
            },
            "name": "LocalhostNetwork",
            "subType": "HOST",
            "type": "networkobject",
            "value": "127.0.0.1",
            "version": "oc2amviloyzed"
        }
    },
...
```

If you want to change the default naming convention, add a `register_as` parameter with the desired fact name to the play.

```yaml
- name: Create network and register as 'localNet'
  ftd_configuration:
    operation: addNetworkObject
    data:
      name: LocalhostNetwork
      subType: HOST
      value: 127.0.0.1
      type: networkobject
    register_as: localNet

- name: Update description
  ftd_configuration:
    operation: editNetworkObject
    data:
      id: '{{ localNet.id }}'
      version: '{{ localNet.version }}'
      name: LocalhostNetwork
      description: Loopback network to access local computer
      subType: HOST
      value: 127.0.0.1
      type: networkobject
    path_params:
      objId: '{{ localNet.id }}'
```

Facts are set on a host-by-host basis. When the playbook is run on multiple devices (hosts), facts are 
visible in a context of a single device (host) only.

## Understanding playbook's idempotency
