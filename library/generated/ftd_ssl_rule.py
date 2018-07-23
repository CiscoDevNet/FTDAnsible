#!/usr/bin/python

# Copyright (c) 2018 Cisco Systems, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'network'}

DOCUMENTATION = """
---
module: ftd_ssl_rule
short_description: Manages SSLRule objects on Cisco FTD devices
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
  certificateStatus
    description:
      - A CertificateStatus object that defines filtering based on server certificate validity<br>Field level constraints: cannot be null. (Note: Additional constraints might exist)
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
      - An optional EmbeddedAppFilter object that defines traffic matching criteria based on application filtering criteria. The object must include SSL-enabled applications only, that is, applications tagged as SSL Protocol.
  eventLogAction
    description:
      - A mandatory EventLogActionSSL object that defines the logging options for the rule.
  filter
    description:
      - The criteria used to filter the models you are requesting. It should have the following format: {field}{operator}{value}[;{field}{operator}{value}]. Supported operators are: "!"(not equals), ":"(equals), "<"(null), "~"(similar), ">"(null). Supported fields are: "name".
  id
    description:
      - A unique string identifier assigned by the system when the object is created. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete (or reference) an existing object.<br>Field level constraints: must match pattern ^((?!;).)*$. (Note: Additional constraints might exist)
  issuerDNs
    description:
      - A list of DistinguishedNameBase objects to filter on based on presented server certificate issuer DN field<br>Allowed types are: [DistinguishedName, DistinguishedNameGroup]
  limit
    description:
      - An integer representing the maximum amount of objects to return. If not specified, the maximum amount is 10
  name
    description:
      - A String object containing the name of the FTDRulebase object. The string can be upto a maximum of 128 characters
  offset
    description:
      - An integer representing the index of the first requested object. Index starts from 0. If not specified, the returned objects will start from index 0
  ruleAction
    description:
      - An enum that specifies the SSL Rule action. Possible values are:<br>DECRYPT_RE_SIGN - Decrypt the traffic, then resign and re-encrypt the content using the configured decryption CA certificate in SSLPolicy.<br>DECRYPT_KNOWN_KEY - Decrypt the traffic going to a host using a known certificate and key. To use known key decryption, you must add the server's certificate and key to the list of known-key certificates in SSLPolicy.<br>DO_NOT_DECRYPT - Do not decrypt the traffic. Encrypted connections are subsequently evaluated by the access control policy, which determines the ultimate allow or block decision.<br>BLOCK - Drop the connection immediately. The connection is not passed on to the access control policy.
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
  sslv3
    description:
      - A Boolean value, TRUE (the default) or FALSE. The TRUE value indicates the rule can be applied to SSL v3 traffic. At least one version of SSL/TLS must be set to TRUE.<br>Field level constraints: cannot be null. (Note: Additional constraints might exist)
  subjectDNs
    description:
      - A list of DistinguishedNameBase objects to filter on based on presented server certificate subject DN field<br>Allowed types are: [DistinguishedName, DistinguishedNameGroup]
  syslogServer
    description:
      - An optional SyslogServer object. Specify a syslog server if you want a copy of events to be sent to an external syslog server.<br>Allowed types are: [SyslogServer]
  tls10
    description:
      - A Boolean value, TRUE (the default) or FALSE. The TRUE value indicates the rule can be applied to TLS v1.0 traffic. At least one version of SSL/TLS must be set to TRUE.<br>Field level constraints: cannot be null. (Note: Additional constraints might exist)
  tls11
    description:
      - A Boolean value, TRUE (the default) or FALSE. The TRUE value indicates the rule can be applied to TLS v1.1 traffic. At least one version of SSL/TLS must be set to TRUE.<br>Field level constraints: cannot be null. (Note: Additional constraints might exist)
  tls12
    description:
      - A Boolean value, TRUE (the default) or FALSE. The TRUE value indicates the rule can be applied to TLS v1.2 traffic. At least one version of SSL/TLS must be set to TRUE.<br>Field level constraints: cannot be null. (Note: Additional constraints might exist)
  type
    description:
      - A UTF8 string, all letters lower-case, that represents the class-type. This corresponds to the class name.
  urlCategories
    description:
      - A list of URLCategoryMatcher objects for rule to filter on<br>Field level constraints: requires URL license. (Note: Additional constraints might exist)
  users
    description:
      - An optional list of TrafficIdentity objects that define traffic matching criteria based on the user or user group that initiated the connection (the source). You must implement an identity policy to use this matching criteria.<br>Allowed types are: [LDAPRealm, ActiveDirectoryRealm, SpecialRealm, LocalIdentitySource, TrafficUser, TrafficUserGroup, User]
  version
    description:
      - A unique string version assigned by the system when the object is created or modified. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete an existing object. As the version will change every time the object is modified, the value provided in this identifier must match exactly what is present in the system or the request will be rejected.
"""

EXAMPLES = """
- name: Fetch SSLRule with a given name
  ftd_ssl_rule:
    operation: "getSSLRuleByName"
    name: "Ansible SSLRule"

- name: Create a SSLRule
  ftd_ssl_rule:
    operation: 'addSSLRule'
    name: "Ansible SSLRule"
    type: "sslrule"
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
from ansible.module_utils.http import iterate_over_pageable_resource
from ansible.module_utils.misc import dict_subset, construct_module_result, copy_identity_properties
from ansible.module_utils.six.moves.urllib.error import HTTPError
from ansible.module_utils.connection import Connection


class SSLRuleResource(object):

    def __init__(self, conn):
        self._conn = conn

    def addSSLRule(self, params):
        path_params = dict_subset(params, ['parentId'])
        query_params = dict_subset(params, ['at'])
        body_params = dict_subset(params, ['certificateStatus', 'destinationNetworks', 'destinationPorts', 'destinationZones', 'embeddedAppFilter', 'eventLogAction', 'id', 'issuerDNs', 'name', 'ruleAction', 'ruleId', 'sourceNetworks', 'sourcePorts', 'sourceZones', 'sslv3', 'subjectDNs', 'syslogServer', 'tls10', 'tls11', 'tls12', 'type', 'urlCategories', 'users', 'version'])

        return self._conn.send_request(
            url_path='/policy/sslpolicies/{parentId}/sslrules',
            http_method='POST',
            body_params=body_params,
            path_params=path_params,
            query_params=query_params,
        )

    def deleteSSLRule(self, params):
        path_params = dict_subset(params, ['objId', 'parentId'])

        return self._conn.send_request(
            url_path='/policy/sslpolicies/{parentId}/sslrules/{objId}',
            http_method='DELETE',
            path_params=path_params,
        )

    def editSSLRule(self, params):
        path_params = dict_subset(params, ['objId', 'parentId'])
        query_params = dict_subset(params, ['at'])
        body_params = dict_subset(params, ['certificateStatus', 'destinationNetworks', 'destinationPorts', 'destinationZones', 'embeddedAppFilter', 'eventLogAction', 'id', 'issuerDNs', 'name', 'ruleAction', 'ruleId', 'sourceNetworks', 'sourcePorts', 'sourceZones', 'sslv3', 'subjectDNs', 'syslogServer', 'tls10', 'tls11', 'tls12', 'type', 'urlCategories', 'users', 'version'])

        return self._conn.send_request(
            url_path='/policy/sslpolicies/{parentId}/sslrules/{objId}',
            http_method='PUT',
            body_params=body_params,
            path_params=path_params,
            query_params=query_params,
        )

    def getSSLRule(self, params):
        path_params = dict_subset(params, ['objId', 'parentId'])

        return self._conn.send_request(
            url_path='/policy/sslpolicies/{parentId}/sslrules/{objId}',
            http_method='GET',
            path_params=path_params,
        )

    def getSSLRuleList(self, params):
        path_params = dict_subset(params, ['parentId'])
        query_params = dict_subset(params, ['filter', 'limit', 'offset', 'sort'])

        return self._conn.send_request(
            url_path='/policy/sslpolicies/{parentId}/sslrules',
            http_method='GET',
            path_params=path_params,
            query_params=query_params,
        )

    def getSSLRuleByName(self, params):
        search_params = params.copy()
        search_params['filter'] = 'name:%s' % params['name']
        item_generator = iterate_over_pageable_resource(self.getSSLRuleList, search_params)
        return next(item for item in item_generator if item['name'] == params['name'])

    def upsertSSLRule(self, params):
        def is_duplicate_name_error(err):
            err_msg = to_text(err.read())
            return err.code == 422 and "Validation failed due to a duplicate name" in err_msg

        try:
            return self.addSSLRule(params)
        except HTTPError as e:
            if is_duplicate_name_error(e):
                existing_object = self.getSSLRuleByName(params)
                params = copy_identity_properties(existing_object, params)
                return self.editSSLRule(params)
            else:
                raise e

    def editSSLRuleByName(self, params):
        existing_object = self.getSSLRuleByName(params)
        params = copy_identity_properties(existing_object, params)
        return self.editSSLRule(params)

    def deleteSSLRuleByName(self, params):
        existing_object = self.getSSLRuleByName(params)
        params = copy_identity_properties(existing_object, params)
        return self.deleteSSLRule(params)


def main():
    fields = dict(
        operation=dict(type='str', default='upsertSSLRule', choices=['addSSLRule', 'deleteSSLRule', 'editSSLRule', 'getSSLRule', 'getSSLRuleList', 'getSSLRuleByName', 'upsertSSLRule', 'editSSLRuleByName', 'deleteSSLRuleByName']),
        register_as=dict(type='str'),

        at=dict(type='int'),
        certificateStatus=dict(type='str'),
        destinationNetworks=dict(type='list'),
        destinationPorts=dict(type='list'),
        destinationZones=dict(type='list'),
        embeddedAppFilter=dict(type='str'),
        eventLogAction=dict(type='str'),
        filter=dict(type='str'),
        id=dict(type='str'),
        issuerDNs=dict(type='list'),
        limit=dict(type='int'),
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
        sslv3=dict(type='bool'),
        subjectDNs=dict(type='list'),
        syslogServer=dict(type='dict'),
        tls10=dict(type='bool'),
        tls11=dict(type='bool'),
        tls12=dict(type='bool'),
        type=dict(type='str'),
        urlCategories=dict(type='list'),
        users=dict(type='list'),
        version=dict(type='str'),
    )

    module = AnsibleModule(argument_spec=fields)
    params = module.params

    try:
        conn = Connection(module._socket_path)
        resource = SSLRuleResource(conn)

        resource_method_to_call = getattr(resource, params['operation'])
        response = resource_method_to_call(params)

        result = construct_module_result(response, params)
        module.exit_json(**result)
    except HTTPError as e:
        err_msg = to_text(e.read())
        module.fail_json(changed=False, msg=json.loads(err_msg) if err_msg else {}, error_code=e.code)
    except Exception as e:
        module.fail_json(changed=False, msg=str(e))


if __name__ == '__main__':
    main()
