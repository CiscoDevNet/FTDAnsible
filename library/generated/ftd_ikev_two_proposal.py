#!/usr/bin/python

# Copyright (c) 2018 Cisco Systems, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'network'}

DOCUMENTATION = """
---
module: ftd_ikev_two_proposal
short_description: Manages IkevTwoProposal objects on Cisco FTD devices
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
  cryptoRestricted
    description:
      - A system-provided Boolean value, TRUE or FALSE. The TRUE value indicates that the proposal uses strong cryptography, which is controlled by export regulations. A device must be registered export-controlled functionality to use a strong encryption proposal.
  defaultAssignable
    description:
      - A system-provided Boolean value, TRUE or FALSE. The TRUE value indicates that the proposal is part of the default set of proposals. The default set differs based on whether the device is registered for export-controlled functionality
  encryptionTypes
    description:
      - A list of enum values that specifies the Encapsulating Security Protocol (ESP) encryption algorithm for this proposal. Specify all algorithms that you want to allow. The system negotiates with the peer, starting from the strongest to the weakest algorithm, until a match is agreed upon. Possible values are, in order of strength:<br>NULL - A null encryption algorithm provides authentication without encryption. This is typically used for testing purposes only.<br>DES - Data Encryption Standard, which encrypts using 56-bit keys, is a symmetric secret-key block algorithm.<br>THREE_DES - Triple DES, which encrypts three times using 56-bit keys.<br>AES - Advanced Encryption Standard is a symmetric cipher algorithm. AES uses 128-bit keys.<br>AES192 - An Advanced Encryption Standard algorithm that uses 192-bit keys.<br>AES256 - An Advanced Encryption Standard algorithm that uses 256-bit keys.<br>AES_GCM - Advanced Encryption Standard in Galois/Counter Mode is a block cipher mode of operation providing confidentiality and data-origin authentication. AES_GCM uses 128-bit keys.<br>AES_GCM192 - An Advanced Encryption Standard in Galois/Counter Mode that uses 192-bit keys.<br>AES_GCM256 - An Advanced Encryption Standard in Galois/Counter Mode that uses 256-bit keys.<br>AES_GMAC - Advanced Encryption Standard Galois Message Authentication Code is a block cipher mode of operation providing only data-origin authentication. AES_GMAC uses 128-bit keys.<br>AES_GMAC192 - An Advanced Encryption Standard Galois Message Authentication Code that uses 192-bit keys.<br>AES_GMAC256 - An Advanced Encryption Standard Galois Message Authentication Code that uses 256-bit keys.
  filter
    description:
      - The criteria used to filter the models you are requesting. It should have the following format: {field}{operator}{value}[;{field}{operator}{value}]. Supported operators are: "!"(not equals), ":"(equals), "<"(null), "~"(similar), ">"(null). Supported fields are: "name".
  id
    description:
      - A unique string identifier assigned by the system when the object is created. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete (or reference) an existing object.<br>Field level constraints: must match pattern ^((?!;).)*$, cannot have HTML. (Note: Additional constraints might exist)
  integrityTypes
    description:
      - A list of enum values that specifies the hash or integrity algorithm to use for authentication. Select all algorithms that you want to allow. The system negotiates with the peer, starting from the strongest to the weakest algorithm, until a match is agreed upon. The integrity hash is not used with the AES-GCM/GMAC encryption options. Possible values are:NULL - A null hash algorithm. This is typically used for testing purposes only. However, you should choose the null integrity algorithm if you select one of the AES-GCM/GMAC options as the encryption algorithm. Even if you choose a non-null option, the integrity hash is ignored for these encryption standards.<br>MD5 - The Message Digest 5 algorithm, which produces a 128-bit digest.<br>SHA1 - The Secure Hash Algorithm, which produces a 160-bit digest.<br>SHA256 - The Secure Hash Algorithm SHA 2 with a 256-bit digest.<br>SHA384 - The Secure Hash Algorithm SHA 2 with a 384-bit digest.<br>SHA512 - The Secure Hash Algorithm SHA 2 with a 512-bit digest.
  isSystemDefined
    description:
      - A Boolean value, TRUE or FALSE (the default). The TRUE value indicates that the system created the object. FALSE indicates that the object is user-defined.
  limit
    description:
      - An integer representing the maximum amount of objects to return. If not specified, the maximum amount is 10
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

extends_documentation_fragment: ftd
"""

EXAMPLES = """
- name: Fetch IkevTwoProposal with a given name
  ftd_ikev_two_proposal:
    hostname: "https://127.0.0.1:8585"
    access_token: 'ACCESS_TOKEN'
    refresh_token: 'REFRESH_TOKEN'
    operation: "getIkevTwoProposalByName"
    name: "Ansible IkevTwoProposal"

- name: Create a IkevTwoProposal
  ftd_ikev_two_proposal:
    hostname: "https://127.0.0.1:8585"
    access_token: 'ACCESS_TOKEN'
    refresh_token: 'REFRESH_TOKEN'
    operation: 'addIkevTwoProposal'

    name: "Ansible IkevTwoProposal"
    type: "ikevtwoproposal"
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
from ansible.module_utils.basic import AnsibleModule, to_text
from ansible.module_utils.http import construct_url, base_headers, iterate_over_pageable_resource
from ansible.module_utils.misc import dict_subset, construct_module_result, copy_identity_properties
from ansible.module_utils.six.moves.urllib.error import HTTPError
from ansible.module_utils.urls import open_url


class IkevTwoProposalResource(object):
    
    @staticmethod
    @retry_on_token_expiration
    def addIkevTwoProposal(params):
        body_params = dict_subset(params, ['cryptoRestricted', 'defaultAssignable', 'encryptionTypes', 'id', 'integrityTypes', 'isSystemDefined', 'name', 'summaryLabel', 'type', 'version'])

        url = construct_url(params['hostname'], '/object/ikev2proposals')
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='POST',
            data=json.dumps(body_params)
        )

        response = open_url(url, **request_params).read()
        return json.loads(to_text(response)) if response else response

    @staticmethod
    @retry_on_token_expiration
    def deleteIkevTwoProposal(params):
        path_params = dict_subset(params, ['objId'])

        url = construct_url(params['hostname'], '/object/ikev2proposals/{objId}', path_params=path_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='DELETE',
        )

        response = open_url(url, **request_params).read()
        return json.loads(to_text(response)) if response else response

    @staticmethod
    @retry_on_token_expiration
    def editIkevTwoProposal(params):
        path_params = dict_subset(params, ['objId'])
        body_params = dict_subset(params, ['cryptoRestricted', 'defaultAssignable', 'encryptionTypes', 'id', 'integrityTypes', 'isSystemDefined', 'name', 'summaryLabel', 'type', 'version'])

        url = construct_url(params['hostname'], '/object/ikev2proposals/{objId}', path_params=path_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='PUT',
            data=json.dumps(body_params)
        )

        response = open_url(url, **request_params).read()
        return json.loads(to_text(response)) if response else response

    @staticmethod
    @retry_on_token_expiration
    def getIkevTwoProposal(params):
        path_params = dict_subset(params, ['objId'])

        url = construct_url(params['hostname'], '/object/ikev2proposals/{objId}', path_params=path_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='GET',
        )

        response = open_url(url, **request_params).read()
        return json.loads(to_text(response)) if response else response

    @staticmethod
    @retry_on_token_expiration
    def getIkevTwoProposalList(params):
        query_params = dict_subset(params, ['filter', 'limit', 'offset', 'sort'])

        url = construct_url(params['hostname'], '/object/ikev2proposals', query_params=query_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='GET',
        )

        response = open_url(url, **request_params).read()
        return json.loads(to_text(response)) if response else response

    @staticmethod
    @retry_on_token_expiration
    def getIkevTwoProposalByName(params):
        search_params = params.copy()
        search_params['filter'] = 'name:%s' % params['name']
        item_generator = iterate_over_pageable_resource(IkevTwoProposalResource.getIkevTwoProposalList, search_params)
        return next(item for item in item_generator if item['name'] == params['name'])

    @staticmethod
    @retry_on_token_expiration
    def upsertIkevTwoProposal(params):
        def is_duplicate_name_error(err):
            err_msg = to_text(err.read())
            return err.code == 422 and "Validation failed due to a duplicate name" in err_msg

        try:
            return IkevTwoProposalResource.addIkevTwoProposal(params)
        except HTTPError as e:
            if is_duplicate_name_error(e):
                existing_object = IkevTwoProposalResource.getIkevTwoProposalByName(params)
                params = copy_identity_properties(existing_object, params)
                return IkevTwoProposalResource.editIkevTwoProposal(params)
            else:
                raise e

    @staticmethod
    @retry_on_token_expiration
    def editIkevTwoProposalByName(params):
        existing_object = IkevTwoProposalResource.getIkevTwoProposalByName(params)
        params = copy_identity_properties(existing_object, params)
        return IkevTwoProposalResource.editIkevTwoProposal(params)

    @staticmethod
    @retry_on_token_expiration
    def deleteIkevTwoProposalByName(params):
        existing_object = IkevTwoProposalResource.getIkevTwoProposalByName(params)
        params = copy_identity_properties(existing_object, params)
        return IkevTwoProposalResource.deleteIkevTwoProposal(params)


def main():
    fields = dict(
        hostname=dict(type='str', required=True),
        access_token=dict(type='str', required=True),
        refresh_token=dict(type='str', required=True),

        operation=dict(type='str', default='upsertIkevTwoProposal', choices=['addIkevTwoProposal', 'deleteIkevTwoProposal', 'editIkevTwoProposal', 'getIkevTwoProposal', 'getIkevTwoProposalList', 'getIkevTwoProposalByName', 'upsertIkevTwoProposal', 'editIkevTwoProposalByName', 'deleteIkevTwoProposalByName']),
        register_as=dict(type='str'),

        cryptoRestricted=dict(type='bool'),
        defaultAssignable=dict(type='bool'),
        encryptionTypes=dict(type='list'),
        filter=dict(type='str'),
        id=dict(type='str'),
        integrityTypes=dict(type='list'),
        isSystemDefined=dict(type='bool'),
        limit=dict(type='int'),
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
        method_to_call = getattr(IkevTwoProposalResource, params['operation'])
        response = method_to_call(params)
        result = construct_module_result(response, params)
        module.exit_json(**result)
    except HTTPError as e:
        err_msg = to_text(e.read())
        module.fail_json(changed=False, msg=json.loads(err_msg) if err_msg else {}, error_code=e.code)
    except Exception as e:
        module.fail_json(changed=False, msg=str(e))


if __name__ == '__main__':
    main()
