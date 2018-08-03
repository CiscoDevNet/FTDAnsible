#!/usr/bin/python

# Copyright (c) 2018 Cisco Systems, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'network'}

DOCUMENTATION = """
---
module: ftd_access_rule
short_description: Manages AccessRule objects on Cisco FTD devices
version_added: "2.7"
author: "Cisco Systems, Inc."
options:
  operation:
    description:
      - Specified the name of the operation to execute in the task.
    required: true
  register_as:
    description:
      - Specifies Ansible fact name that is used to register received response from the FTD device.
  at
    description:
      - An integer representing where to add the new object in the ordered list. Use 0 to add it at the beginning of the list. If not specified, it will be added at the end of the list
  destinationNetworks
    description:
      - A Set of Network objects considered as a destination network.<br>Allowed types are: [Continent, Country, GeoLocation, NetworkObject, NetworkObjectGroup]
  destinationPorts
    description:
      - A Set of PortObjectBase objects considered as a destination port.<br>Allowed types are: [ICMPv4PortObject, ICMPv6PortObject, ProtocolObject, TCPPortObject, UDPPortObject, PortObjectGroup]
  destinationZones
    description:
      - A Set of ZoneBase objects considered considered as a destination zone.<br>Allowed types are: [SecurityZone, TunnelZone]
  embeddedAppFilter
    description:
      - An optional EmbeddedAppFilter object. Providing an object will make the rule be applied only to traffic matching provided app filter's condition(s).
  eventLogAction
    description:
      - A mandatory EventLogAction object that defines the logging options for the rule.
  filePolicy
    description:
      - An optional FilePolicy object. Providing an object will make the rul be applied only to traffic matching the provided file policy's condition(s).<br>Field level constraints: requires malware license. (Note: Additional constraints might exist)<br>Allowed types are: [FilePolicy]
  filter
    description:
      - The criteria used to filter the models you are requesting. It should have the following format: {field}{operator}{value}[;{field}{operator}{value}]. Supported operators are: "!"(not equals), ":"(equals), "<"(null), "~"(similar), ">"(null). Supported fields are: "name".
  id
    description:
      - A unique string identifier assigned by the system when the object is created. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete (or reference) an existing object.<br>Field level constraints: must match pattern ^((?!;).)*$. (Note: Additional constraints might exist)
  intrusionPolicy
    description:
      - An optional IntrusionPolicy object. Specify an IntrusionPolicy object if you would like the traffic passing through the rule be inspected by the IP object.<br>Field level constraints: requires threat license. (Note: Additional constraints might exist)<br>Allowed types are: [IntrusionPolicy]
  limit
    description:
      - An integer representing the maximum amount of objects to return. If not specified, the maximum amount is 10
  logFiles
    description:
      - An optional Boolean object. Logs files matching to the current rule if set to true. Default option is false
  name
    description:
      - A String object containing the name of the FTDRulebase object. The string can be upto a maximum of 128 characters
  offset
    description:
      - An integer representing the index of the first requested object. Index starts from 0. If not specified, the returned objects will start from index 0
  ruleAction
    description:
      - A mandatory AcRuleAction object that defines the Access Control Rule action. Possible values are:<br>PERMIT <br>TRUST <br>DENY
  ruleId
    description:
      - A non editable Long object which holds the rule ID number of the FTDRulebase object. It is created by the system in the POST request, and the same value must be included in the PUT request.
  sort
    description:
      - The field used to sort the requested object list
  sourceNetworks
    description:
      - A Set of Network objects considered as a source network.<br>Allowed types are: [Continent, Country, GeoLocation, NetworkObject, NetworkObjectGroup]
  sourcePorts
    description:
      - A Set of PortObjectBase objects considered as a source port.<br>Allowed types are: [ICMPv4PortObject, ICMPv6PortObject, ProtocolObject, TCPPortObject, UDPPortObject, PortObjectGroup]
  sourceZones
    description:
      - A Set of ZoneBase objects considered as a source zone.<br>Allowed types are: [SecurityZone, TunnelZone]
  syslogServer
    description:
      - An optional SyslogServer object. Specify a syslog server if you want a copy of events matching the current rule to be sent to an external syslog server.<br>Allowed types are: [SyslogServer]
  type
    description:
      - A UTF8 string, all letters lower-case, that represents the class-type. This corresponds to the class name.
  urlFilter
    description:
      - An optional EmbeddedURLFilter object. Providing an object will make the rule be applied only to traffic matching provided url filter's condition(s).
  users
    description:
      - A Set object containing TrafficIdentity objects. A TrafficIdentity object represents a User/Group of an Active Directory(AD).<br>Allowed types are: [LDAPRealm, ActiveDirectoryRealm, SpecialRealm, LocalIdentitySource, TrafficUser, TrafficUserGroup, User]
  version
    description:
      - A unique string version assigned by the system when the object is created or modified. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete an existing object. As the version will change every time the object is modified, the value provided in this identifier must match exactly what is present in the system or the request will be rejected.
"""

EXAMPLES = """
- name: Fetch AccessRule with a given name
  ftd_access_rule:
    operation: "getAccessRuleByName"
    name: "Ansible AccessRule"

- name: Create a AccessRule
  ftd_access_rule:
    operation: 'addAccessRule'
    name: "Ansible AccessRule"
    sourceNetworks: ["{{ networkObject }}"]
    type: "accessrule"
    parentId: "default"
"""

RETURN = """
response:
  description: HTTP response returned from the API call.
  returned: success
  type: dict
error_code:
  description: HTTP error code returned from the server.
  returned: error
  type: int
msg:
  description: Error message returned from the server.
  returned: error
  type: dict
"""
import json

from ansible.module_utils.basic import AnsibleModule, to_text
from ansible.module_utils.config_resource import BaseConfigObjectResource
from ansible.module_utils.connection import Connection
from ansible.module_utils.misc import dict_subset, construct_ansible_facts, copy_identity_properties
from ansible.module_utils.six.moves.urllib.error import HTTPError


class AccessRuleResource(BaseConfigObjectResource):

    def addAccessRule(self, params):
        path_params = dict_subset(params, ['parentId'])
        query_params = dict_subset(params, ['at'])
        body_params = dict_subset(params, ['destinationNetworks', 'destinationPorts', 'destinationZones', 'embeddedAppFilter', 'eventLogAction', 'filePolicy', 'id', 'intrusionPolicy', 'logFiles', 'name', 'ruleAction', 'ruleId', 'sourceNetworks', 'sourcePorts', 'sourceZones', 'syslogServer', 'type', 'urlFilter', 'users', 'version'])

        return self.add_object(
            url_path='/policy/accesspolicies/{parentId}/accessrules',
            body_params=body_params,
            path_params=path_params,
            query_params=query_params,
        )

    def deleteAccessRule(self, params):
        path_params = dict_subset(params, ['objId', 'parentId'])

        return self.delete_object(
            url_path='/policy/accesspolicies/{parentId}/accessrules/{objId}',
            path_params=path_params,
        )

    def editAccessRule(self, params):
        path_params = dict_subset(params, ['objId', 'parentId'])
        query_params = dict_subset(params, ['at'])
        body_params = dict_subset(params, ['destinationNetworks', 'destinationPorts', 'destinationZones', 'embeddedAppFilter', 'eventLogAction', 'filePolicy', 'id', 'intrusionPolicy', 'logFiles', 'name', 'ruleAction', 'ruleId', 'sourceNetworks', 'sourcePorts', 'sourceZones', 'syslogServer', 'type', 'urlFilter', 'users', 'version'])

        return self.edit_object(
            url_path='/policy/accesspolicies/{parentId}/accessrules/{objId}',
            body_params=body_params,
            path_params=path_params,
            query_params=query_params,
        )

    def getAccessRule(self, params):
        path_params = dict_subset(params, ['objId', 'parentId'])

        return self._conn.send_request(
            url_path='/policy/accesspolicies/{parentId}/accessrules/{objId}',
            http_method='GET',
            path_params=path_params,
        )

    def getAccessRuleList(self, params):
        path_params = dict_subset(params, ['parentId'])
        query_params = dict_subset(params, ['filter', 'limit', 'offset', 'sort'])

        return self._conn.send_request(
            url_path='/policy/accesspolicies/{parentId}/accessrules',
            http_method='GET',
            path_params=path_params,
            query_params=query_params,
        )

    def getAccessRuleByName(self, params):
        return self.get_object_by_name(
            url_path='/policy/accesspolicies/{parentId}/accessrules',
            path_params=dict_subset(params, ['parentId']),
            name=params['name']
        )

    def upsertAccessRule(self, params):
        path_params = dict_subset(params, ['parentId'])
        query_params = dict_subset(params, ['at'])
        body_params = dict_subset(params, ['destinationNetworks', 'destinationPorts', 'destinationZones', 'embeddedAppFilter', 'eventLogAction', 'filePolicy', 'id', 'intrusionPolicy', 'logFiles', 'name', 'ruleAction', 'ruleId', 'sourceNetworks', 'sourcePorts', 'sourceZones', 'syslogServer', 'type', 'urlFilter', 'users', 'version'])

        return self.add_object(
            url_path='/policy/accesspolicies/{parentId}/accessrules',
            body_params=body_params,
            path_params=path_params,
            query_params=query_params,
            update_if_exists=True
        )

    def editAccessRuleByName(self, params):
        existing_object = self.getAccessRuleByName(params)
        params = copy_identity_properties(existing_object, params)
        params['objId'] = existing_object['id']
        return self.editAccessRule(params)

    def deleteAccessRuleByName(self, params):
        existing_object = self.getAccessRuleByName(params)
        params = copy_identity_properties(existing_object, params)
        params['objId'] = existing_object['id']
        return self.deleteAccessRule(params)


def main():
    fields = dict(
        operation=dict(type='str', default='upsertAccessRule', choices=['addAccessRule', 'deleteAccessRule', 'editAccessRule', 'getAccessRule', 'getAccessRuleList', 'getAccessRuleByName', 'upsertAccessRule', 'editAccessRuleByName', 'deleteAccessRuleByName']),
        register_as=dict(type='str'),

        at=dict(type='int'),
        destinationNetworks=dict(type='list'),
        destinationPorts=dict(type='list'),
        destinationZones=dict(type='list'),
        embeddedAppFilter=dict(type='str'),
        eventLogAction=dict(type='str'),
        filePolicy=dict(type='dict'),
        filter=dict(type='str'),
        id=dict(type='str'),
        intrusionPolicy=dict(type='dict'),
        limit=dict(type='int'),
        logFiles=dict(type='bool'),
        name=dict(type='str'),
        objId=dict(type='str'),
        offset=dict(type='int'),
        parentId=dict(type='str'),
        ruleAction=dict(type='str'),
        ruleId=dict(type='int'),
        sort=dict(type='str'),
        sourceNetworks=dict(type='list'),
        sourcePorts=dict(type='list'),
        sourceZones=dict(type='list'),
        syslogServer=dict(type='dict'),
        type=dict(type='str'),
        urlFilter=dict(type='str'),
        users=dict(type='list'),
        version=dict(type='str'),
    )

    module = AnsibleModule(argument_spec=fields)
    params = module.params

    try:
        conn = Connection(module._socket_path)
        resource = AccessRuleResource(conn)

        resource_method_to_call = getattr(resource, params['operation'])
        response = resource_method_to_call(params)
        module.exit_json(changed=resource.config_changed, response=response,
                         ansible_facts=construct_ansible_facts(response, params))
    except HTTPError as e:
        err_msg = to_text(e.read())
        module.fail_json(changed=False, msg=json.loads(err_msg) if err_msg else {}, error_code=e.code)
    except Exception as e:
        module.fail_json(changed=False, msg=str(e))


if __name__ == '__main__':
    main()
