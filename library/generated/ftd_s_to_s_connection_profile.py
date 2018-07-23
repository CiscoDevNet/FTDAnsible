#!/usr/bin/python

# Copyright (c) 2018 Cisco Systems, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'network'}

DOCUMENTATION = """
---
module: ftd_s_to_s_connection_profile
short_description: Manages SToSConnectionProfile objects on Cisco FTD devices
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
  diffieHellmanGroup
    description:
      - An enum value that defines the Diffie-Hellman group to use for Perfect Forwarding Secrecy. If left empty, Perfect Forward Secrecy is disabled. Possible values are:<br>GROUP1 - 768-bit modulus.<br>GROUP2 - 1024-bit modulus.<br>GROUP5 - 1536-bit modulus.<br>GROUP14 - 2048 bit modulus.<br>GROUP19 - 256 bit elliptic curve.<br>GROUP20 - 384 bit elliptic curve.<br>GROUP21 - 521 bit elliptic curve.<br>GROUP24 - 2048-bit modulus and 256-bit prime order subgroup.
  filter
    description:
      - The criteria used to filter the models you are requesting. It should have the following format: {field}{operator}{value}[;{field}{operator}{value}]. Supported operators are: "!"(not equals), ":"(equals), "<"(null), "~"(similar), ">"(null). Supported fields are: "name".
  id
    description:
      - A unique string identifier assigned by the system when the object is created. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete (or reference) an existing object.<br>Field level constraints: must match pattern ^((?!;).)*$. (Note: Additional constraints might exist)
  ikev1Enabled
    description:
      - A mandatory Boolean value, TRUE (default) or FALSE. The TRUE value indicates that IKEv1 will be used by the VPN tunnel in connection attempts and negotiations. Note that if both IKEv1 and IKEv2 are enabled, IKEv2 will be used first.<br>Field level constraints: cannot be null. (Note: Additional constraints might exist)
  ikev1PreSharedKey
    description:
      - A string containing the pre-shared key for IKE v1 connections. This is mandatory if IKEv1 is enabled. The key is encrypted when stored in the system, and the system will return a generic string instead of the key string for security reasons.
  ikev1Proposals
    description:
      - A list of IkevOneProposal objects to be used in IKEv1 connections. The list cannot be empty if IKEv1 is enabled.<br>Allowed types are: [IkevOneProposal]
  ikev2Enabled
    description:
      - A mandatory Boolean value, TRUE (default) or FALSE. The TRUE value indicates that IKEv2 will be used by the VPN tunnel in connection attempts and negotiations. Note that if both IKEv1 and IKEv2 are enabled, IKEv2 will be used first.<br>Field level constraints: cannot be null. (Note: Additional constraints might exist)
  ikev2LocalPreSharedKey
    description:
      - A string containing the local pre-shared key for IKE v2 connections. This is mandatory if IKEv2 is enabled. The key is encrypted when stored in the system, and the system will return a generic string instead of the key string for security reasons.
  ikev2Proposals
    description:
      - A list of IkevTwoProposal objects to be used in IKEv2 connections. The list cannot be empty if IKEv2 is enabled.<br>Allowed types are: [IkevTwoProposal]
  ikev2RemotePeerPreSharedKey
    description:
      - A string containing the remote pre-shared key for IKE v2 connections. This is mandatory if IKEv2 is enabled. The key is encrypted when stored in the system, and the system will return a generic string instead of the key string for security reasons.
  interfaceForNatExempt
    description:
      - A PhysicalInterface or SubInterface object that needs a NAT exempt rule generated for access through VPN. If left empty, no NAT exempt rules will be automatically generated.<br>Allowed types are: [PhysicalInterface, SubInterface]
  limit
    description:
      - An integer representing the maximum amount of objects to return. If not specified, the maximum amount is 10
  localNetworks
    description:
      - A list of NetworkObject or NetworkObjectGroup objects of the source of the traffic that is to be routed through the VPN tunnel. If no source networks are provided, then traffic from any source may be forwarded through the tunnel.<br>Allowed types are: [NetworkObject, NetworkObjectGroup]
  name
    description:
      - A string containing the name of the VPN profile. The string can be up to 50 characters, but can only consist of alphanumeric characters and the following special characters: _.+-
  offset
    description:
      - An integer representing the index of the first requested object. Index starts from 0. If not specified, the returned objects will start from index 0
  outsideInterfaces
    description:
      - A mandatory list of a single PhysicalInterface or SubInterface object that can be used for establishing the VPN connection. The list must contain only one object.<br>Field level constraints: cannot be null. (Note: Additional constraints might exist)<br>Allowed types are: [PhysicalInterface, SubInterface]
  remoteNetworks
    description:
      - A list of NetworkObject or NetworkObjectGroup objects of the destination of the traffic that is to be routed through the VPN tunnel. If no remote networks are provided, then traffic going to any destination may be forwarded through the tunnel.<br>Allowed types are: [NetworkObject, NetworkObjectGroup]
  remotePeerIpAddress
    description:
      - A mandatory string that contains the IP address of the site-to-site VPN peer to connect to<br>Field level constraints: cannot be null, must be a valid IP address. (Note: Additional constraints might exist)
  sort
    description:
      - The field used to sort the requested object list
  type
    description:
      - A UTF8 string, all letters lower-case, that represents the class-type. This corresponds to the class name.
  version
    description:
      - A unique string version assigned by the system when the object is created or modified. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete an existing object. As the version will change every time the object is modified, the value provided in this identifier must match exactly what is present in the system or the request will be rejected.
"""

EXAMPLES = """
- name: Fetch SToSConnectionProfile with a given name
  ftd_s_to_s_connection_profile:
    operation: "getSToSConnectionProfileByName"
    name: "Ansible SToSConnectionProfile"

- name: Create a SToSConnectionProfile
  ftd_s_to_s_connection_profile:
    operation: 'addSToSConnectionProfile'
    name: "Ansible SToSConnectionProfile"
    type: "stosconnectionprofile"
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


class SToSConnectionProfileResource(object):

    def __init__(self, conn):
        self._conn = conn

    def addSToSConnectionProfile(self, params):
        body_params = dict_subset(params, ['diffieHellmanGroup', 'id', 'ikev1Enabled', 'ikev1PreSharedKey', 'ikev1Proposals', 'ikev2Enabled', 'ikev2LocalPreSharedKey', 'ikev2Proposals', 'ikev2RemotePeerPreSharedKey', 'interfaceForNatExempt', 'localNetworks', 'name', 'outsideInterfaces', 'remoteNetworks', 'remotePeerIpAddress', 'type', 'version'])

        return self._conn.send_request(
            url_path='/devices/default/s2sconnectionprofiles',
            http_method='POST',
            body_params=body_params,
        )

    def deleteSToSConnectionProfile(self, params):
        path_params = dict_subset(params, ['objId'])

        return self._conn.send_request(
            url_path='/devices/default/s2sconnectionprofiles/{objId}',
            http_method='DELETE',
            path_params=path_params,
        )

    def editSToSConnectionProfile(self, params):
        path_params = dict_subset(params, ['objId'])
        body_params = dict_subset(params, ['diffieHellmanGroup', 'id', 'ikev1Enabled', 'ikev1PreSharedKey', 'ikev1Proposals', 'ikev2Enabled', 'ikev2LocalPreSharedKey', 'ikev2Proposals', 'ikev2RemotePeerPreSharedKey', 'interfaceForNatExempt', 'localNetworks', 'name', 'outsideInterfaces', 'remoteNetworks', 'remotePeerIpAddress', 'type', 'version'])

        return self._conn.send_request(
            url_path='/devices/default/s2sconnectionprofiles/{objId}',
            http_method='PUT',
            body_params=body_params,
            path_params=path_params,
        )

    def getSToSConnectionProfile(self, params):
        path_params = dict_subset(params, ['objId'])

        return self._conn.send_request(
            url_path='/devices/default/s2sconnectionprofiles/{objId}',
            http_method='GET',
            path_params=path_params,
        )

    def getSToSConnectionProfileList(self, params):
        query_params = dict_subset(params, ['filter', 'limit', 'offset', 'sort'])

        return self._conn.send_request(
            url_path='/devices/default/s2sconnectionprofiles',
            http_method='GET',
            query_params=query_params,
        )

    def getSToSConnectionProfileByName(self, params):
        search_params = params.copy()
        search_params['filter'] = 'name:%s' % params['name']
        item_generator = iterate_over_pageable_resource(self.getSToSConnectionProfileList, search_params)
        return next(item for item in item_generator if item['name'] == params['name'])

    def upsertSToSConnectionProfile(self, params):
        def is_duplicate_name_error(err):
            err_msg = to_text(err.read())
            return err.code == 422 and "Validation failed due to a duplicate name" in err_msg

        try:
            return self.addSToSConnectionProfile(params)
        except HTTPError as e:
            if is_duplicate_name_error(e):
                existing_object = self.getSToSConnectionProfileByName(params)
                params = copy_identity_properties(existing_object, params)
                return self.editSToSConnectionProfile(params)
            else:
                raise e

    def editSToSConnectionProfileByName(self, params):
        existing_object = self.getSToSConnectionProfileByName(params)
        params = copy_identity_properties(existing_object, params)
        return self.editSToSConnectionProfile(params)

    def deleteSToSConnectionProfileByName(self, params):
        existing_object = self.getSToSConnectionProfileByName(params)
        params = copy_identity_properties(existing_object, params)
        return self.deleteSToSConnectionProfile(params)


def main():
    fields = dict(
        operation=dict(type='str', default='upsertSToSConnectionProfile', choices=['addSToSConnectionProfile', 'deleteSToSConnectionProfile', 'editSToSConnectionProfile', 'getSToSConnectionProfile', 'getSToSConnectionProfileList', 'getSToSConnectionProfileByName', 'upsertSToSConnectionProfile', 'editSToSConnectionProfileByName', 'deleteSToSConnectionProfileByName']),
        register_as=dict(type='str'),

        diffieHellmanGroup=dict(type='str'),
        filter=dict(type='str'),
        id=dict(type='str'),
        ikev1Enabled=dict(type='bool'),
        ikev1PreSharedKey=dict(type='str'),
        ikev1Proposals=dict(type='list'),
        ikev2Enabled=dict(type='bool'),
        ikev2LocalPreSharedKey=dict(type='str'),
        ikev2Proposals=dict(type='list'),
        ikev2RemotePeerPreSharedKey=dict(type='str'),
        interfaceForNatExempt=dict(type='dict'),
        limit=dict(type='int'),
        localNetworks=dict(type='list'),
        name=dict(type='str'),
        objId=dict(type='str'),
        offset=dict(type='int'),
        outsideInterfaces=dict(type='list'),
        remoteNetworks=dict(type='list'),
        remotePeerIpAddress=dict(type='str'),
        sort=dict(type='str'),
        type=dict(type='str'),
        version=dict(type='str'),
    )

    module = AnsibleModule(argument_spec=fields)
    params = module.params

    try:
        conn = Connection(module._socket_path)
        resource = SToSConnectionProfileResource(conn)

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
