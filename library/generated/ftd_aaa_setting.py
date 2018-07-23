#!/usr/bin/python

# Copyright (c) 2018 Cisco Systems, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'network'}

DOCUMENTATION = """
---
module: ftd_aaa_setting
short_description: Manages AAASetting objects on Cisco FTD devices
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
  description
    description:
      - This referenced identity source group object will be used for the external authentication of the specified connection type<br>Field level constraints: must match pattern ^((?!;).)*$, length must be between 0 and 200 (inclusive). (Note: Additional constraints might exist)
  filter
    description:
      - The criteria used to filter the models you are requesting. It should have the following format: {field}{operator}{value}[;{field}{operator}{value}]. Supported operators are: "!"(not equals), ":"(equals), "<"(null), "~"(similar), ">"(null). Supported fields are: "name".
  id
    description:
      - A unique string identifier assigned by the system when the object is created. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete (or reference) an existing object.<br>Field level constraints: must match pattern ^((?!;).)*$. (Note: Additional constraints might exist)
  identitySourceGroup
    description:
      -  Reference to a AAA Identity Source group object.<br>Field level constraints: cannot be null. (Note: Additional constraints might exist)<br>Allowed types are: [IdentitySourceBase, LDAPRealm, ActiveDirectoryRealm, SpecialRealm, LocalIdentitySource, RadiusIdentitySource, RadiusIdentitySourceGroup]
  limit
    description:
      - An integer representing the maximum amount of objects to return. If not specified, the maximum amount is 10
  name
    description:
      - A read-only string specifying the name of the rule.
  offset
    description:
      - An integer representing the index of the first requested object. Index starts from 0. If not specified, the returned objects will start from index 0
  protocolType
    description:
      - A read-only enum that defines the protocol type for the AAA Identity Source. The default value is HTTPS. The possible values for this object are: <br>HTTPS<br>SSH<br>Field level constraints: cannot be null. (Note: Additional constraints might exist)
  sort
    description:
      - The field used to sort the requested object list
  type
    description:
      - A UTF8 string, all letters lower-case, that represents the class-type. This corresponds to the class name.
  useLocal
    description:
      - An enum that specifies the order in which the system will use local authentication if the identity sources are unreachable. If the rule's identity source group is set to local, then this field should be set to NOT_APPLICABLE. Otherwise, the field should be set to either BEFORE, AFTER, or NEVER.<br>Field level constraints: cannot be null. (Note: Additional constraints might exist)
  version
    description:
      - A unique string version assigned by the system when the object is created or modified. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete an existing object. As the version will change every time the object is modified, the value provided in this identifier must match exactly what is present in the system or the request will be rejected.
"""

EXAMPLES = """
- name: Fetch AAASetting with a given name
  ftd_aaa_setting:
    operation: "getAAASettingByName"
    name: "Ansible AAASetting"
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


class AAASettingResource(object):

    def __init__(self, conn):
        self._conn = conn

    def editAAASetting(self, params):
        path_params = dict_subset(params, ['objId'])
        body_params = dict_subset(params, ['description', 'id', 'identitySourceGroup', 'name', 'protocolType', 'type', 'useLocal', 'version'])

        return self._conn.send_request(
            url_path='/devicesettings/default/aaasettings/{objId}',
            http_method='PUT',
            body_params=body_params,
            path_params=path_params,
        )

    def getAAASetting(self, params):
        path_params = dict_subset(params, ['objId'])

        return self._conn.send_request(
            url_path='/devicesettings/default/aaasettings/{objId}',
            http_method='GET',
            path_params=path_params,
        )

    def getAAASettingList(self, params):
        query_params = dict_subset(params, ['filter', 'limit', 'offset', 'sort'])

        return self._conn.send_request(
            url_path='/devicesettings/default/aaasettings',
            http_method='GET',
            query_params=query_params,
        )

    def getAAASettingByName(self, params):
        search_params = params.copy()
        search_params['filter'] = 'name:%s' % params['name']
        item_generator = iterate_over_pageable_resource(self.getAAASettingList, search_params)
        return next(item for item in item_generator if item['name'] == params['name'])

    def editAAASettingByName(self, params):
        existing_object = self.getAAASettingByName(params)
        params = copy_identity_properties(existing_object, params)
        return self.editAAASetting(params)


def main():
    fields = dict(
        operation=dict(type='str', choices=['editAAASetting', 'getAAASetting', 'getAAASettingList', 'getAAASettingByName', 'editAAASettingByName'], required=True),
        register_as=dict(type='str'),

        description=dict(type='str'),
        filter=dict(type='str'),
        id=dict(type='str'),
        identitySourceGroup=dict(type='dict'),
        limit=dict(type='int'),
        name=dict(type='str'),
        objId=dict(type='str'),
        offset=dict(type='int'),
        protocolType=dict(type='str'),
        sort=dict(type='str'),
        type=dict(type='str'),
        useLocal=dict(type='str'),
        version=dict(type='str'),
    )

    module = AnsibleModule(argument_spec=fields)
    params = module.params

    try:
        conn = Connection(module._socket_path)
        resource = AAASettingResource(conn)

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
