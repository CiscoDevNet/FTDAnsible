# Examples

Here are some examples that demonstrate how to use Ansible modules for common 
operations on FTD devices. Hopefully, they will make the process of creating 
your playbooks easier.

## Create a NetworkObject

This example demonstrates how to create a simple entity representing a network - 
`NetworkObject`. The task creates a new object representing a fully qualified 
domain name (FQDN) network for [Cisco DevNet](https://developer.cisco.com/) website.

After creation, the network object is stored as an Ansible fact and can be accessed
using `networkobject_ciscodevnetnetwork` variable. 

```yaml
- name: Create an FQDN network for Cisco DevNet
  ftd_configuration:
    operation: "addNetworkObject"
    data:
      name: "CiscoDevNetNetwork"
      subType: "FQDN"
      value: "developer.cisco.com"
      isSystemDefined: False
      type: "networkobject"
      dnsResolution: "IPV4_AND_IPV6"
```

## Create a NetworkObjectGroup

`NetworkObjectGroup` is a container object representing a group of networks.

The first task creates an auxiliary `NetworkObject` for [Cisco Meraki](https://meraki.cisco.com/)
website. Then, a `NetworkObjectGroup`, consisting of two previously created networks,
is created in the second task.

Notice, that the second task, creating a `NetworkObjectGroup` object, references previously 
created `NetworkObject`s. It is possible because every created object is stored as an Ansible fact.
By default, an object gets registered in a `TYPE_NAME` fact, but the fact's name can be
modified in a `register_as` parameter. 

```yaml
- name: Create an FQDN network for Cisco Meraki
  ftd_configuration:
    operation: "addNetworkObject"
    data:
      name: "CiscoMerakiNetwork"
      subType: "FQDN"
      value: "meraki.cisco.com"
      isSystemDefined: False
      type: "networkobject"
      dnsResolution: "IPV4_AND_IPV6"

- name: Create a Cisco network group
  ftd_configuration:
    operation: "addNetworkObjectGroup"
    data:
      name: "CiscoNetworkGroup"
      type: "networkobjectgroup"
      objects:
        - "{{ networkobject_ciscodevnetnetwork }}"
        - "{{ networkobject_ciscomerakinetwork }}"
```

## Create an AccessRule

An `AccessRule` permits or denies traffic based on different parameters, such as a protocol,
a source or destination IP address, network, etc.

The example shows how to create an `AccessRule` allowing traffic from the previously created
`CiscoNetworkGroup`.

```yaml
- name: Create an access rule allowing trafic from CiscoNetworkGroup
  ftd_configuration:
    operation: "addAccessRule"
    data:
      name: "AllowCiscoTraffic"
      type: "accessrule"
      sourceNetworks:
        - "{{ networkobjectgroup_cisconetworkgroup }}"
      ruleAction: "PERMIT"
      eventLogAction: "LOG_BOTH"
    path_params:
      parentId: "default"
 ```

## Make a deployment

Changes made on the FTD device are applied only after they get deployed. This example demonstrates
how to start a deployment job and make sure that it succeeds.

The first task starts a new deployment job and registers returned `DeploymentStatus` as `deployment_job` Ansible fact.
The next task polls the `DeploymentStatus` every 3 seconds until the job is completed. The last
part verifies that the deployment is completed successfully. Otherwise, it stops the playbook with an error message.

```yaml
- name: Start deployment
  ftd_configuration:
    operation: "addDeployment"
    register_as: "deployment_job"

- name: Poll deployment status until the job is finished
  ftd_configuration:
    operation: "getDeployment"
    path_params:
      objId: "{{ deployment_job['id'] }}"
    register_as: "deployment_status"
  until: deployment_status['endTime'] != -1
  retries: 100
  delay: 3

- name: Stop the playbook if the deployment failed
  fail:
    msg: "Deployment failed. Status: {{ deployment_status['statusMessages'] }}"
  when: deployment_status['state'] != 'DEPLOYED'
```

