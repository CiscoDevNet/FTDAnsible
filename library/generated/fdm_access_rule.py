#!/usr/bin/python

# Copyright (c) 2018 Cisco Systems, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'network'}

DOCUMENTATION = """
---
module: fdm_access_rule
short_description: Manages AccessRule objects on Cisco FTD devices with FDM
version_added: "2.7"
author: "Cisco Systems, Inc."
options:
  hostname:
    description:
      - Specifies the hostname of the FTD device.
    required: true
  access_token:
    description:
      - Specifies the token to access the FTD device.
    required: true
  refresh_token:
    description:
      - Specifies the token to refresh the access token when the current one expires.
    required: true
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
      - A unique string identifier assigned by the system when the object is created. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete (or reference) an existing object.<br>Field level constraints: must match pattern ^((?!;).)*$, cannot have HTML. (Note: Additional constraints might exist)
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
      - A Long object which holds the rule ID number of the FTDRulebase object.
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
      - A Set object containing TrafficIdentity objects. A TrafficIdentity object represents a User/Group of an Active Directory(AD).<br>Allowed types are: [LDAPRealm, ActiveDirectoryRealm, SpecialRealm, TrafficUser, TrafficUserGroup]
  version
    description:
      - A unique string version assigned by the system when the object is created or modified. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete an existing object. As the version will change every time the object is modified, the value provided in this identifier must match exactly what is present in the system or the request will be rejected.
  vlanTags
    description:
      - A Set object of VlanTags associated with the rule.<br>Allowed types are: [VlanTag, VlanTagGroup]
"""

EXAMPLES = """
- name: Create an access rule
  fdm_access_policy:
    hostname: "https://localhost:8585"
    access_token: 'ACCESS_TOKEN'
    refresh_token: 'REFRESH_TOKEN'
    operation: 'addAccessRule'
    name: "Ansible-accessrule"
    type: "accessrule"
    parentId: "default"
    sourceNetworks:
      - "{{ networkObj1 }}"
    register_as: "accessRule1"
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

from ansible.module_utils.authorization import retry_on_token_expiration
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.http import construct_url, base_headers, iterate_over_pageable_resource
from ansible.module_utils.misc import dict_subset, construct_module_result
from ansible.module_utils.six.moves.urllib.error import HTTPError
from ansible.module_utils.urls import open_url


class AccessRuleResource(object):
    
    @staticmethod
    @retry_on_token_expiration
    def addAccessRule(params):
        path_params = dict_subset(params, ['parentId'])
        query_params = dict_subset(params, ['at'])
        body_params = dict_subset(params, ['version', 'name', 'ruleId', 'sourceZones', 'destinationZones', 'sourceNetworks', 'destinationNetworks', 'sourcePorts', 'destinationPorts', 'ruleAction', 'eventLogAction', 'vlanTags', 'users', 'embeddedAppFilter', 'urlFilter', 'intrusionPolicy', 'filePolicy', 'logFiles', 'syslogServer', 'id', 'type'])

        url = construct_url(params['hostname'], '/policy/accesspolicies/{parentId}/accessrules', path_params=path_params, query_params=query_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='POST',
            data=json.dumps(body_params)
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def deleteAccessRule(params):
        path_params = dict_subset(params, ['parentId', 'objId'])

        url = construct_url(params['hostname'], '/policy/accesspolicies/{parentId}/accessrules/{objId}', path_params=path_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='DELETE',
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def editAccessRule(params):
        path_params = dict_subset(params, ['parentId', 'objId'])
        query_params = dict_subset(params, ['at'])
        body_params = dict_subset(params, ['version', 'name', 'ruleId', 'sourceZones', 'destinationZones', 'sourceNetworks', 'destinationNetworks', 'sourcePorts', 'destinationPorts', 'ruleAction', 'eventLogAction', 'vlanTags', 'users', 'embeddedAppFilter', 'urlFilter', 'intrusionPolicy', 'filePolicy', 'logFiles', 'syslogServer', 'id', 'type'])

        url = construct_url(params['hostname'], '/policy/accesspolicies/{parentId}/accessrules/{objId}', path_params=path_params, query_params=query_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='PUT',
            data=json.dumps(body_params)
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def getAccessRule(params):
        path_params = dict_subset(params, ['parentId', 'objId'])

        url = construct_url(params['hostname'], '/policy/accesspolicies/{parentId}/accessrules/{objId}', path_params=path_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='GET',
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def getAccessRuleList(params):
        path_params = dict_subset(params, ['parentId'])
        query_params = dict_subset(params, ['offset', 'limit', 'sort', 'filter'])

        url = construct_url(params['hostname'], '/policy/accesspolicies/{parentId}/accessrules', path_params=path_params, query_params=query_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='GET',
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def getAccessRuleByName(params):
        search_params = params.copy()
        search_params['filter'] = 'name:%s' % params['name']
        item_generator = iterate_over_pageable_resource(AccessRuleResource.getAccessRuleList, search_params)
        return next(item for item in item_generator if item['name'] == params['name'])

    @staticmethod
    @retry_on_token_expiration
    def upsertAccessRule(params):
        def is_duplicate_name_error(err):
            return err.code == 422 and "Validation failed due to a duplicate name" in str(err.read())

        try:
            return AccessRuleResource.addAccessRule(params)
        except HTTPError as e:
            if is_duplicate_name_error(e):
                existing_object = AccessRuleResource.getAccessRuleByName(params)
                params = AccessRuleResource.copy_identity_params(existing_object, params)
                return AccessRuleResource.editAccessRule(params)
            else:
                raise e

    @staticmethod
    @retry_on_token_expiration
    def editAccessRuleByName(params):
        existing_object = AccessRuleResource.getAccessRuleByName(params)
        params = AccessRuleResource.copy_identity_params(existing_object, params)
        return AccessRuleResource.editAccessRule(params)

    @staticmethod
    @retry_on_token_expiration
    def deleteAccessRuleByName(params):
        existing_object = AccessRuleResource.getAccessRuleByName(params)
        params = AccessRuleResource.copy_identity_params(existing_object, params)
        return AccessRuleResource.deleteAccessRule(params)

    @staticmethod
    def copy_identity_params(source_object, dest_params):
        dest_params['objId'] = source_object['id']
        dest_params['id'] = source_object['id']
        if 'version' in source_object:
            dest_params['version'] = source_object['version']
        dest_params['ruleId'] = source_object.get('ruleId')
        return dest_params


def main():
    fields = dict(
        hostname=dict(type='str', required=True),
        access_token=dict(type='str', required=True),
        refresh_token=dict(type='str', required=True),

        operation=dict(choices=['addAccessRule', 'deleteAccessRule', 'editAccessRule', 'getAccessRule', 'getAccessRuleList', 'getAccessRuleByName', 'upsertAccessRule', 'editAccessRuleByName', 'deleteAccessRuleByName'], required=True),
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
        vlanTags=dict(type='list'),
    )

    module = AnsibleModule(argument_spec=fields)
    params = module.params

    try:
        method_to_call = getattr(AccessRuleResource, params['operation'])
        response = method_to_call(params)
        result = construct_module_result(response, params)
        module.exit_json(**result)
    except HTTPError as e:
        err_msg = e.read()
        module.fail_json(changed=False, msg=json.loads(err_msg) if err_msg else {}, error_code=e.code)
    except Exception as e:
        module.fail_json(changed=False, msg=str(e))


if __name__ == '__main__':
    main()
