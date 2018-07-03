#!/usr/bin/python

# Copyright (c) 2018 Cisco Systems, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'network'}

DOCUMENTATION = """
---
module: fdm_ikev_two_policy
short_description: Manages IkevTwoPolicy objects on Cisco FTD devices with FDM
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
      - A system-provided Boolean value, TRUE or FALSE. The TRUE value indicates that the policy uses strong cryptography, which is controlled by export regulations. A device must be registered export-controlled functionality to use a strong encryption policy.
  enabled
    description:
      - A mandatory Boolean value, TRUE or FALSE (the default). The TRUE value enables the policy, which means remote peers can use it when negotiating a site-to-site VPN connection. FALSE indicates that although the policy is defined, remote peers cannot negotiate connections based on the policy.<br>Field level constraints: cannot be null. (Note: Additional constraints might exist)
  encryptionTypes
    description:
      - A list of enum values that specifies the encryption algorithm used to establish the Phase 1 security association (SA) for protecting Phase 2 negotiations. Specify all algorithms that you want to allow, although you cannot include both mixed-mode (AES-GCM) and normal mode options in the same policy. (Normal mode requires that you select an integrity hash, whereas mixed mode prohibits a separate integrity hash selection.) The system negotiates with the peer, starting from the strongest to the weakest algorithm, until a match is agreed upon. Possible values are, in order of strength:<br>NULL - A null encryption algorithm provides authentication without encryption. This is typically used for testing purposes only.<br>DES - Data Encryption Standard, which encrypts using 56-bit keys, is a symmetric secret-key block algorithm.<br>THREE_DES - Triple DES, which encrypts three times using 56-bit keys.<br>AES - Advanced Encryption Standard is a symmetric cipher algorithm. AES uses 128--bit keys.<br>AES192 - An Advanced Encryption Standard algorithm that uses 192--bit keys.<br>AES256 - An Advanced Encryption Standard algorithm that uses 256--bit keys.<br>AES_GCM - Advanced Encryption Standard in Galois/Counter Mode is a block cipher mode of operation providing confidentiality and data-origin authentication. AES_GCM uses 128-bit keys.<br>AES_GCM192 - An Advanced Encryption Standard in Galois/Counter Mode that uses 192-bit keys.<br>AES_GCM256 - An Advanced Encryption Standard in Galois/Counter Mode that uses 256-bit keys.
  filter
    description:
      - The criteria used to filter the models you are requesting. It should have the following format: {field}{operator}{value}[;{field}{operator}{value}]. Supported operators are: "!"(not equals), ":"(equals), "<"(null), "~"(similar), ">"(null). Supported fields are: "name".
  groupTypes
    description:
      - A list of enum values that specifies the Diffie-Hellman group to use for deriving a shared secret between the two IPsec peers without transmitting it to each other. A larger modulus provides higher security but requires more processing time. The two peers must have a matching modulus group. Specify all algorithms that you want to allow. The system negotiates with the peer, starting from the strongest to the weakest group, until a match is agreed upon. Possible values are:<br>GROUP1 - 768-bit modulus.<br>GROUP2 - 1024-bit modulus.<br>GROUP5 - 1536-bit modulus.<br>GROUP14 - 2048 bit modulus.<br>GROUP19 - 256 bit elliptic curve.<br>GROUP20 - 384 bit elliptic curve.<br>GROUP21 - 521 bit elliptic curve.<br>GROUP24 - 2048-bit modulus and 256-bit prime order subgroup.
  id
    description:
      - A unique string identifier assigned by the system when the object is created. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete (or reference) an existing object.<br>Field level constraints: must match pattern ^((?!;).)*$, cannot have HTML. (Note: Additional constraints might exist)
  integrityTypes
    description:
      - A list of enum values that specifies the integrity portion of the hash algorithm for creating a message digest, which is used to ensure message integrity. Select all algorithms that you want to allow. The system negotiates with the peer, starting from the strongest to the weakest algorithm, until a match is agreed upon. The integrity hash is not used with the AES-GCM encryption options. Possible values are:<br>NULL - A null hash algorithm. This is typically used for testing purposes only. However, you should choose the null integrity algorithm if you select one of the AES-GCM/GMAC options as the encryption algorithm. Even if you choose a non-null option, the integrity hash is ignored for these encryption standards.<br>MD5 - The Message Digest 5 algorithm, which produces a 128-bit digest.<br>SHA - The Secure Hash Algorithm, which produces a 160-bit digest.<br>SHA256 - The Secure Hash Algorithm SHA 2 with a 256-bit digest.<br>SHA384 - The Secure Hash Algorithm SHA 2 with a 384-bit digest.<br>SHA512 - The Secure Hash Algorithm SHA 2 with a 512-bit digest.
  isSystemDefined
    description:
      - A Boolean value, TRUE or FALSE (the default). The TRUE value indicates that the system created the object. FALSE indicates that the object is user-defined.
  lifeTime
    description:
      - An optional integer that defines the lifetime of the security association (SA), in seconds, from 120 to 2147483647, with the typical limit being 86400. When the lifetime is exceeded, the SA expires and must be renegotiated between the two peers. Leave the option as null to specify no lifetime limit.
  limit
    description:
      - An integer representing the maximum amount of objects to return. If not specified, the maximum amount is 10
  name
    description:
      - The name of the object, up to 128 characters.
  offset
    description:
      - An integer representing the index of the first requested object. Index starts from 0. If not specified, the returned objects will start from index 0
  prfTypes
    description:
      - A list of enum values that specifies the pseudo-random function (PRF) portion of the hash algorithm, which is used as the algorithm to derive keying material and hashing operations required for the IKEv2 tunnel encryption. Select all algorithms that you want to allow. The system negotiates with the peer, starting from the strongest to the weakest algorithm, until a match is agreed upon. Possible values are:<br>MD5 - The Message Digest 5 algorithm, which produces a 128-bit digest.<br>SHA - The Secure Hash Algorithm, which produces a 160-bit digest.<br>SHA256 - The Secure Hash Algorithm SHA 2 with a 256-bit digest.<br>SHA384 - The Secure Hash Algorithm SHA 2 with a 384-bit digest.<br>SHA512 - The Secure Hash Algorithm SHA 2 with a 512-bit digest.
  priority
    description:
      - A required integer that determines the relative priority of the IKE policy, from 1 to 65535. The priority determines the order of the IKE policy compared by the two negotiating peers when attempting to find a common security association (SA). If the remote IPsec peer does not support the parameters selected in your highest priority policy, it tries to use the parameters defined in the next lowest priority. The lower the number, the higher the priority. A given number is meaningful only in relation to the priority numbers defined on the other IKE policies.<br>Field level constraints: cannot be null. (Note: Additional constraints might exist)
  sort
    description:
      - The field used to sort the requested object list
  summaryLabel
    description:
      - A system-provided string that describes the IKE policy.
  type
    description:
      - A UTF8 string, all letters lower-case, that represents the class-type. This corresponds to the class name.
  version
    description:
      - A unique string version assigned by the system when the object is created or modified. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete an existing object. As the version will change every time the object is modified, the value provided in this identifier must match exactly what is present in the system or the request will be rejected.

extends_documentation_fragment: fdm
"""

EXAMPLES = """
- name: Fetch IkevTwoPolicy with a given name
  fdm_ikev_two_policy:
    hostname: "https://127.0.0.1:8585"
    access_token: 'ACCESS_TOKEN'
    refresh_token: 'REFRESH_TOKEN'
    operation: "getIkevTwoPolicyByName"
    name: "Ansible IkevTwoPolicy"

- name: Create a IkevTwoPolicy
  fdm_ikev_two_policy:
    hostname: "https://127.0.0.1:8585"
    access_token: 'ACCESS_TOKEN'
    refresh_token: 'REFRESH_TOKEN'
    operation: 'addIkevTwoPolicy'

    name: "Ansible IkevTwoPolicy"
    type: "ikevtwopolicy"
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
from ansible.module_utils.misc import dict_subset, construct_module_result, copy_identity_properties
from ansible.module_utils.six.moves.urllib.error import HTTPError
from ansible.module_utils.urls import open_url


class IkevTwoPolicyResource(object):
    
    @staticmethod
    @retry_on_token_expiration
    def addIkevTwoPolicy(params):
        body_params = dict_subset(params, ['version', 'name', 'enabled', 'lifeTime', 'priority', 'encryptionTypes', 'groupTypes', 'integrityTypes', 'prfTypes', 'summaryLabel', 'cryptoRestricted', 'id', 'isSystemDefined', 'type'])

        url = construct_url(params['hostname'], '/object/ikev2policies')
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='POST',
            data=json.dumps(body_params)
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def deleteIkevTwoPolicy(params):
        path_params = dict_subset(params, ['objId'])

        url = construct_url(params['hostname'], '/object/ikev2policies/{objId}', path_params=path_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='DELETE',
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def editIkevTwoPolicy(params):
        path_params = dict_subset(params, ['objId'])
        body_params = dict_subset(params, ['version', 'name', 'enabled', 'lifeTime', 'priority', 'encryptionTypes', 'groupTypes', 'integrityTypes', 'prfTypes', 'summaryLabel', 'cryptoRestricted', 'id', 'isSystemDefined', 'type'])

        url = construct_url(params['hostname'], '/object/ikev2policies/{objId}', path_params=path_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='PUT',
            data=json.dumps(body_params)
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def getIkevTwoPolicy(params):
        path_params = dict_subset(params, ['objId'])

        url = construct_url(params['hostname'], '/object/ikev2policies/{objId}', path_params=path_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='GET',
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def getIkevTwoPolicyList(params):
        query_params = dict_subset(params, ['offset', 'limit', 'sort', 'filter'])

        url = construct_url(params['hostname'], '/object/ikev2policies', query_params=query_params)
        request_params = dict(
            headers=base_headers(params['access_token']),
            method='GET',
        )

        response = open_url(url, **request_params).read()
        return json.loads(response) if response else response

    @staticmethod
    @retry_on_token_expiration
    def getIkevTwoPolicyByName(params):
        search_params = params.copy()
        search_params['filter'] = 'name:%s' % params['name']
        item_generator = iterate_over_pageable_resource(IkevTwoPolicyResource.getIkevTwoPolicyList, search_params)
        return next(item for item in item_generator if item['name'] == params['name'])

    @staticmethod
    @retry_on_token_expiration
    def upsertIkevTwoPolicy(params):
        def is_duplicate_name_error(err):
            return err.code == 422 and "Validation failed due to a duplicate name" in str(err.read())

        try:
            return IkevTwoPolicyResource.addIkevTwoPolicy(params)
        except HTTPError as e:
            if is_duplicate_name_error(e):
                existing_object = IkevTwoPolicyResource.getIkevTwoPolicyByName(params)
                params = copy_identity_properties(existing_object, params)
                return IkevTwoPolicyResource.editIkevTwoPolicy(params)
            else:
                raise e

    @staticmethod
    @retry_on_token_expiration
    def editIkevTwoPolicyByName(params):
        existing_object = IkevTwoPolicyResource.getIkevTwoPolicyByName(params)
        params = copy_identity_properties(existing_object, params)
        return IkevTwoPolicyResource.editIkevTwoPolicy(params)

    @staticmethod
    @retry_on_token_expiration
    def deleteIkevTwoPolicyByName(params):
        existing_object = IkevTwoPolicyResource.getIkevTwoPolicyByName(params)
        params = copy_identity_properties(existing_object, params)
        return IkevTwoPolicyResource.deleteIkevTwoPolicy(params)


def main():
    fields = dict(
        hostname=dict(type='str', required=True),
        access_token=dict(type='str', required=True),
        refresh_token=dict(type='str', required=True),

        operation=dict(choices=['addIkevTwoPolicy', 'deleteIkevTwoPolicy', 'editIkevTwoPolicy', 'getIkevTwoPolicy', 'getIkevTwoPolicyList', 'getIkevTwoPolicyByName', 'upsertIkevTwoPolicy', 'editIkevTwoPolicyByName', 'deleteIkevTwoPolicyByName'], required=True),
        register_as=dict(type='str'),

        cryptoRestricted=dict(type='bool'),
        enabled=dict(type='bool'),
        encryptionTypes=dict(type='list'),
        filter=dict(type='str'),
        groupTypes=dict(type='list'),
        id=dict(type='str'),
        integrityTypes=dict(type='list'),
        isSystemDefined=dict(type='bool'),
        lifeTime=dict(type='int'),
        limit=dict(type='int'),
        name=dict(type='str'),
        objId=dict(type='str'),
        offset=dict(type='int'),
        prfTypes=dict(type='list'),
        priority=dict(type='int'),
        sort=dict(type='str'),
        summaryLabel=dict(type='str'),
        type=dict(type='str'),
        version=dict(type='str'),
    )

    module = AnsibleModule(argument_spec=fields)
    params = module.params

    try:
        method_to_call = getattr(IkevTwoPolicyResource, params['operation'])
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
