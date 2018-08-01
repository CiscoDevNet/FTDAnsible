#!/usr/bin/python

# Copyright (c) 2018 Cisco Systems, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'network'}

DOCUMENTATION = """
---
module: ftd_access_policy
short_description: Manages AccessPolicy objects on Cisco FTD devices
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
  defaultAction
    description:
      - An optional AccessDefaultAction. Provide an AccessDefaultAction object to set a default action to AccessPolicy.
  filter
    description:
      - The criteria used to filter the models you are requesting. It should have the following format: {field}{operator}{value}[;{field}{operator}{value}]. Supported operators are: "!"(not equals), ":"(equals), "<"(null), "~"(similar), ">"(null). Supported fields are: "name".
  id
    description:
      - A unique string identifier assigned by the system when the object is created. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete (or reference) an existing object.<br>Field level constraints: must match pattern ^((?!;).)*$. (Note: Additional constraints might exist)
  identityPolicySetting
    description:
      - An optional IdentityPolicy object. Provide an IdentityPolicy object to associate with the given AccessPolicy.<br>Allowed types are: [IdentityPolicy]
  limit
    description:
      - An integer representing the maximum amount of objects to return. If not specified, the maximum amount is 10
  name
    description:
      - A string containing the name of the Access Policy. The string should not contain HTML content.
  offset
    description:
      - An integer representing the index of the first requested object. Index starts from 0. If not specified, the returned objects will start from index 0
  securityIntelligence
    description:
      - An optional SecurityIntelligencePolicy. Provide a SecurityIntelligencePolicy object to associate with the given AccessPolicy<br>Field level constraints: requires threat license. (Note: Additional constraints might exist)<br>Allowed types are: [SecurityIntelligencePolicy]
  sort
    description:
      - The field used to sort the requested object list
  sslPolicy
    description:
      - An optional SSLPolicy object. Provide a SSLPolicy object to associate with the given AccessPolicy<br>Allowed types are: [SSLPolicy]
  type
    description:
      - A UTF8 string, all letters lower-case, that represents the class-type. This corresponds to the class name.
  version
    description:
      - A unique string version assigned by the system when the object is created or modified. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete an existing object. As the version will change every time the object is modified, the value provided in this identifier must match exactly what is present in the system or the request will be rejected.
"""

EXAMPLES = """
- name: Fetch AccessPolicy with a given name
  ftd_access_policy:
    operation: "getAccessPolicyByName"
    name: "Ansible AccessPolicy"
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


class AccessPolicyResource(BaseConfigObjectResource):

    def editAccessPolicy(self, params):
        path_params = dict_subset(params, ['objId'])
        body_params = dict_subset(params, ['defaultAction', 'id', 'identityPolicySetting', 'name', 'securityIntelligence', 'sslPolicy', 'type', 'version'])

        return self.edit_object(
            url_path='/policy/accesspolicies/{objId}',
            body_params=body_params,
            path_params=path_params,
        )

    def getAccessPolicy(self, params):
        path_params = dict_subset(params, ['objId'])

        return self._conn.send_request(
            url_path='/policy/accesspolicies/{objId}',
            http_method='GET',
            path_params=path_params,
        )

    def getAccessPolicyList(self, params):
        query_params = dict_subset(params, ['filter', 'limit', 'offset', 'sort'])

        return self._conn.send_request(
            url_path='/policy/accesspolicies',
            http_method='GET',
            query_params=query_params,
        )

    def getAccessPolicyByName(self, params):
        return self.get_object_by_name(
            url_path='/policy/accesspolicies',
            name=params['name']
        )

    def editAccessPolicyByName(self, params):
        existing_object = self.getAccessPolicyByName(params)
        params = copy_identity_properties(existing_object, params)
        return self.editAccessPolicy(params)


def main():
    fields = dict(
        operation=dict(type='str', choices=['editAccessPolicy', 'getAccessPolicy', 'getAccessPolicyList', 'getAccessPolicyByName', 'editAccessPolicyByName'], required=True),
        register_as=dict(type='str'),

        defaultAction=dict(type='str'),
        filter=dict(type='str'),
        id=dict(type='str'),
        identityPolicySetting=dict(type='dict'),
        limit=dict(type='int'),
        name=dict(type='str'),
        objId=dict(type='str'),
        offset=dict(type='int'),
        securityIntelligence=dict(type='dict'),
        sort=dict(type='str'),
        sslPolicy=dict(type='dict'),
        type=dict(type='str'),
        version=dict(type='str'),
    )

    module = AnsibleModule(argument_spec=fields)
    params = module.params

    try:
        conn = Connection(module._socket_path)
        resource = AccessPolicyResource(conn)

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
