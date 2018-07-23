#!/usr/bin/python

# Copyright (c) 2018 Cisco Systems, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'network'}

DOCUMENTATION = """
---
module: ftd_license
short_description: Manages License objects on Cisco FTD devices
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
  compliant
    description:
      - A read only Boolean object, TRUE or FALSE. The value TRUE indicates if the license exists in the account. The value FALSE indicates if the license is expired or there are not enough of that license type in the account.
  count
    description:
      - A mandatory Integer object, must be 1, specifies the number of Licenses for a particular License Type. <br>Field level constraints: cannot be null, must be between 1 and 1 (inclusive). (Note: Additional constraints might exist)
  filter
    description:
      - The criteria used to filter the models you are requesting. It should have the following format: {field}{operator}{value}[;{field}{operator}{value}]. Supported operators are: "!"(not equals), ":"(equals), "<"(null), "~"(similar), ">"(null). Supported fields are: "name".
  id
    description:
      - A unique string identifier assigned by the system when the object is created. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete (or reference) an existing object.<br>Field level constraints: must match pattern ^((?!;).)*$. (Note: Additional constraints might exist)
  licenseType
    description:
      - A mandatory enum that specifies the type of Licensing. The values can be one of the following. You can use any of the AnyConnect Licenses: PLUS, APEX or VPNOnly for enabling RA VPN. <br> BASE - Default license that comes with the device and all features not covered by the optional term licenses. <br> MALWARE - Enables the file policies that check for malware. <br> THREAT - Enables Intrusion detection and prevention. <br> URLFILTERING - Enables Category and reputation-based URL filtering. <br> APEX - Enables licensing for RAVPN. <br> PLUS - Enables licensing for RAVPN. <br> VPNOnly - Enables licensing for RAVPN.<br>Field level constraints: cannot be null. (Note: Additional constraints might exist)
  limit
    description:
      - An integer representing the maximum amount of objects to return. If not specified, the maximum amount is 10
  offset
    description:
      - An integer representing the index of the first requested object. Index starts from 0. If not specified, the returned objects will start from index 0
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
- name: Fetch License with a given name
  ftd_license:
    operation: "getLicenseByName"
    name: "Ansible License"

- name: Create a License
  ftd_license:
    operation: 'addLicense'
    type: "license"
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


class LicenseResource(object):

    def __init__(self, conn):
        self._conn = conn

    def addLicense(self, params):
        body_params = dict_subset(params, ['compliant', 'count', 'id', 'licenseType', 'type', 'version'])

        return self._conn.send_request(
            url_path='/license/smartlicenses',
            http_method='POST',
            body_params=body_params,
        )

    def deleteLicense(self, params):
        path_params = dict_subset(params, ['objId'])

        return self._conn.send_request(
            url_path='/license/smartlicenses/{objId}',
            http_method='DELETE',
            path_params=path_params,
        )

    def getLicense(self, params):
        path_params = dict_subset(params, ['objId'])

        return self._conn.send_request(
            url_path='/license/smartlicenses/{objId}',
            http_method='GET',
            path_params=path_params,
        )

    def getLicenseList(self, params):
        query_params = dict_subset(params, ['filter', 'limit', 'offset', 'sort'])

        return self._conn.send_request(
            url_path='/license/smartlicenses',
            http_method='GET',
            query_params=query_params,
        )

    def getLicenseByName(self, params):
        search_params = params.copy()
        search_params['filter'] = 'name:%s' % params['name']
        item_generator = iterate_over_pageable_resource(self.getLicenseList, search_params)
        return next(item for item in item_generator if item['name'] == params['name'])

    def deleteLicenseByName(self, params):
        existing_object = self.getLicenseByName(params)
        params = copy_identity_properties(existing_object, params)
        return self.deleteLicense(params)


def main():
    fields = dict(
        operation=dict(type='str', choices=['addLicense', 'deleteLicense', 'getLicense', 'getLicenseList', 'getLicenseByName', 'deleteLicenseByName'], required=True),
        register_as=dict(type='str'),

        compliant=dict(type='bool'),
        count=dict(type='int'),
        filter=dict(type='str'),
        id=dict(type='str'),
        licenseType=dict(type='str'),
        limit=dict(type='int'),
        objId=dict(type='str'),
        offset=dict(type='int'),
        sort=dict(type='str'),
        type=dict(type='str'),
        version=dict(type='str'),
    )

    module = AnsibleModule(argument_spec=fields)
    params = module.params

    try:
        conn = Connection(module._socket_path)
        resource = LicenseResource(conn)

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
