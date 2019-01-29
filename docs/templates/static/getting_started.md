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
          type: networkobject
```

More examples can be found [here](./examples.md).

## Understanding upsert operation

Upsert is idempotent "Insert or Update" operation which came from [Database world](https://en.wikipedia.org/wiki/Merge_\(SQL\)). 
It allows You to define the desired state of the record without check if the record exists(so should be updated) or not(so should be created). 
As result usage of this operation allows You define your playbook as:

```yaml
- hosts: all
  connection: httpapi
  tasks:
    - name: Upsert localhost network
      ftd_configuration:
        operation: upsertNetworkObject
        data:
          name: LocalhostNetwork
          subType: HOST
          value: 127.0.0.1
          type: networkobject
```

instead of:

```yaml
- hosts: all
  connection: httpapi
  tasks:
    - name: Get localhost networks
      ftd_configuration:
        operation: getNetworkObjectList
        query_params:
          filter: name~LocalhostNetwork
        register_as: my_networks
    - name: Create localhost network does not exists
      ftd_configuration:
        operation: addNetworkObject
        data:
          name: LocalhostNetwork
          subType: HOST
          value: 127.0.0.1
          type: networkobject
      when: my_networks.0 is undefined
    - name: Update localhost network if exists already
      ftd_configuration:
        operation: editNetworkObject
        data:
          name: LocalhostNetwork
          subType: HOST
          value: 127.0.0.1
          type: networkobject
        path_params:
          objId: "{{ my_networks[0].id }}"
      when: my_networks.0 is not undefined
```

## Registering objects as Ansible facts

In order to reuse objects in subsequent plays during an ansible-playbook run, they should be registered as variables. 
FTD modules automatically register server responses as Ansible _facts_. Then, these _facts_ can be used in the playbook as 
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

## Understanding operation's idempotency

An operation is _idempotent_ if the result of running it once is exactly the same as the result of running it 
multiple times. As Ansible requires modules to be idempotent, `ftd_configuration` complies with this requirement.

Before executing the operation, `ftd_configuration` checks whether the desired final state is already achieved. 
If yes, no actions are executed, and the operation finishes showing that the state is not changed. 

For example, when running `addNetworkObject` operation multiple times without changing the play configuration, 
only the first run results in `changed` status. Subsequent runs are finished with `ok` status.

```
$ ansible-playbook test.yml

TASK [Create localhost network] *******************************************
changed: [localhost]

PLAY RECAP ****************************************************************
localhost               : ok=1    changed=1    unreachable=0    failed=0

$ ansible-playbook test.yml

TASK [Create localhost network] *******************************************
ok: [localhost]

PLAY RECAP ****************************************************************
localhost               : ok=1    changed=0    unreachable=0    failed=0
``` 

When playbook tasks are idempotent, the playbook itself must be idempotent too. Having idempotent playbook is 
recommended, as it allows to re-run them safely.
