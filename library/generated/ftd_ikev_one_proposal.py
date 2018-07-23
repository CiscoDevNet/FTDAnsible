#!/usr/bin/python

# Copyright (c) 2018 Cisco Systems, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'network'}

DOCUMENTATION = """
---
module: ftd_ikev_one_proposal
short_description: Manages IkevOneProposal objects on Cisco FTD devices
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
  authenticationMethod
    description:
      - An enum value that specifies the hash or integrity algorithm to use for authentication. Possible values are:<br>ESP_NONE - A null hash algorithm. This is typically used for testing purposes only.<br>ESP_MD5_HMAC - The Message Digest 5 algorithm, which produces a 128-bit digest.<br>ESP_SHA_HMAC - The Secure Hash Algorithm, which produces a 160-bit digest.<br>Field level constraints: cannot be null. (Note: Additional constraints might exist)
  cryptoRestricted
    description:
      - A system-provided Boolean value, TRUE or FALSE. The TRUE value indicates that the proposal uses strong cryptography, which is controlled by export regulations. A device must be registered export-controlled functionality to use a strong encryption proposal.
  defaultAssignable
    description:
      - A system-provided Boolean value, TRUE or FALSE. The TRUE value indicates that the proposal is part of the default set of proposals. The default set differs based on whether the device is registered for export-controlled functionality
  encryptionMethod
    description:
      - An enum value that specifies the Encapsulating Security Protocol (ESP) encryption algorithm for this proposal. Possible values are, in order of strength:<br>ESP_NULL - A null encryption algorithm provides authentication without encryption. This is typically used for testing purposes only.<br>ESP_DES - Data Encryption Standard, which encrypts using 56-bit keys, is a symmetric secret-key block algorithm.<br>ESP_THREE_DES - Triple DES, which encrypts three times using 56-bit keys.<br>ESP_AES - Advanced Encryption Standard is a symmetric cipher algorithm. AES uses 128-bit keys.<br>ESP_AES192 - An Advanced Encryption Standard algorithm that uses 192-bit keys.<br>ESP_AES256 - An Advanced Encryption Standard algorithm that uses 256-bit keys.<br>Field level constraints: cannot be null. (Note: Additional constraints might exist)
  filter
    description:
      - The criteria used to filter the models you are requesting. It should have the following format: {field}{operator}{value}[;{field}{operator}{value}]. Supported operators are: "!"(not equals), ":"(equals), "<"(null), "~"(similar), ">"(null). Supported fields are: "name".
  id
    description:
      - A unique string identifier assigned by the system when the object is created. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete (or reference) an existing object.<br>Field level constraints: must match pattern ^((?!;).)*$. (Note: Additional constraints might exist)
  isSystemDefined
    description:
      - A Boolean value, TRUE or FALSE (the default). The TRUE value indicates that the system created the object. FALSE indicates that the object is user-defined.
  limit
    description:
      - An integer representing the maximum amount of objects to return. If not specified, the maximum amount is 10
  mode
    description:
      - An enum value that specifies the mode in which the IPSec tunnel operates. Possible values are:<br>TUNNEL (the default) - Tunnel mode encapsulates the entire IP packet. The IPSec header is added between the original IP header and a new IP header. Use tunnel mode when the firewall is protecting traffic to and from hosts positioned behind the firewall. Tunnel mode is the normal way regular IPSec is implemented between two firewalls (or other security gateways) that are connected over an untrusted network, such as the Internet.<br>TRANSPORT - Transport mode encapsulates only the upper-layer protocols of an IP packet. The IPSec header is inserted between the IP header and the upper-layer protocol header (such as TCP). Transport mode requires that both the source and destination hosts support IPSec, and can only be used when the destination peer of the tunnel is the final destination of the IP packet. Transport mode is generally used only when protecting a Layer 2 or Layer 3 tunneling protocol such as GRE, L2TP, and DLSW.<br>Field level constraints: cannot be null. (Note: Additional constraints might exist)
  name
    description:
      - The name of the object, up to 64 characters.
  offset
    description:
      - An integer representing the index of the first requested object. Index starts from 0. If not specified, the returned objects will start from index 0
  sort
    description:
      - The field used to sort the requested object list
  summaryLabel
    description:
      - A system-provided string that describes the IKE proposal.
  type
    description:
      - A UTF8 string, all letters lower-case, that represents the class-type. This corresponds to the class name.
  version
    description:
      - A unique string version assigned by the system when the object is created or modified. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete an existing object. As the version will change every time the object is modified, the value provided in this identifier must match exactly what is present in the system or the request will be rejected.
"""

EXAMPLES = """
- name: Fetch IkevOneProposal with a given name
  ftd_ikev_one_proposal:
    operation: "getIkevOneProposalByName"
    name: "Ansible IkevOneProposal"

- name: Create a IkevOneProposal
  ftd_ikev_one_proposal:
    operation: 'addIkevOneProposal'
    name: "Ansible IkevOneProposal"
    type: "ikevoneproposal"
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


class IkevOneProposalResource(object):

    def __init__(self, conn):
        self._conn = conn

    def addIkevOneProposal(self, params):
        body_params = dict_subset(params, ['authenticationMethod', 'cryptoRestricted', 'defaultAssignable', 'encryptionMethod', 'id', 'isSystemDefined', 'mode', 'name', 'summaryLabel', 'type', 'version'])

        return self._conn.send_request(
            url_path='/object/ikev1proposals',
            http_method='POST',
            body_params=body_params,
        )

    def deleteIkevOneProposal(self, params):
        path_params = dict_subset(params, ['objId'])

        return self._conn.send_request(
            url_path='/object/ikev1proposals/{objId}',
            http_method='DELETE',
            path_params=path_params,
        )

    def editIkevOneProposal(self, params):
        path_params = dict_subset(params, ['objId'])
        body_params = dict_subset(params, ['authenticationMethod', 'cryptoRestricted', 'defaultAssignable', 'encryptionMethod', 'id', 'isSystemDefined', 'mode', 'name', 'summaryLabel', 'type', 'version'])

        return self._conn.send_request(
            url_path='/object/ikev1proposals/{objId}',
            http_method='PUT',
            body_params=body_params,
            path_params=path_params,
        )

    def getIkevOneProposal(self, params):
        path_params = dict_subset(params, ['objId'])

        return self._conn.send_request(
            url_path='/object/ikev1proposals/{objId}',
            http_method='GET',
            path_params=path_params,
        )

    def getIkevOneProposalList(self, params):
        query_params = dict_subset(params, ['filter', 'limit', 'offset', 'sort'])

        return self._conn.send_request(
            url_path='/object/ikev1proposals',
            http_method='GET',
            query_params=query_params,
        )

    def getIkevOneProposalByName(self, params):
        search_params = params.copy()
        search_params['filter'] = 'name:%s' % params['name']
        item_generator = iterate_over_pageable_resource(self.getIkevOneProposalList, search_params)
        return next(item for item in item_generator if item['name'] == params['name'])

    def upsertIkevOneProposal(self, params):
        def is_duplicate_name_error(err):
            err_msg = to_text(err.read())
            return err.code == 422 and "Validation failed due to a duplicate name" in err_msg

        try:
            return self.addIkevOneProposal(params)
        except HTTPError as e:
            if is_duplicate_name_error(e):
                existing_object = self.getIkevOneProposalByName(params)
                params = copy_identity_properties(existing_object, params)
                return self.editIkevOneProposal(params)
            else:
                raise e

    def editIkevOneProposalByName(self, params):
        existing_object = self.getIkevOneProposalByName(params)
        params = copy_identity_properties(existing_object, params)
        return self.editIkevOneProposal(params)

    def deleteIkevOneProposalByName(self, params):
        existing_object = self.getIkevOneProposalByName(params)
        params = copy_identity_properties(existing_object, params)
        return self.deleteIkevOneProposal(params)


def main():
    fields = dict(
        operation=dict(type='str', default='upsertIkevOneProposal', choices=['addIkevOneProposal', 'deleteIkevOneProposal', 'editIkevOneProposal', 'getIkevOneProposal', 'getIkevOneProposalList', 'getIkevOneProposalByName', 'upsertIkevOneProposal', 'editIkevOneProposalByName', 'deleteIkevOneProposalByName']),
        register_as=dict(type='str'),

        authenticationMethod=dict(type='str'),
        cryptoRestricted=dict(type='bool'),
        defaultAssignable=dict(type='bool'),
        encryptionMethod=dict(type='str'),
        filter=dict(type='str'),
        id=dict(type='str'),
        isSystemDefined=dict(type='bool'),
        limit=dict(type='int'),
        mode=dict(type='str'),
        name=dict(type='str'),
        objId=dict(type='str'),
        offset=dict(type='int'),
        sort=dict(type='str'),
        summaryLabel=dict(type='str'),
        type=dict(type='str'),
        version=dict(type='str'),
    )

    module = AnsibleModule(argument_spec=fields)
    params = module.params

    try:
        conn = Connection(module._socket_path)
        resource = IkevOneProposalResource(conn)

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
