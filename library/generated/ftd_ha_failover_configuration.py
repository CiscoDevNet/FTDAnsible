#!/usr/bin/python

# Copyright (c) 2018 Cisco Systems, Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'network'}

DOCUMENTATION = """
---
module: ftd_ha_failover_configuration
short_description: Manages HAFailoverConfiguration objects on Cisco FTD devices
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
  filter
    description:
      - The criteria used to filter the models you are requesting. It should have the following format: {field}{operator}{value}[;{field}{operator}{value}]. Supported operators are: "!"(not equals), ":"(equals), "<"(null), "~"(similar), ">"(null). Supported fields are: "name".
  id
    description:
      - A unique string identifier assigned by the system when the object is created. No assumption can be made on the format or content of this identifier. The identifier must be provided whenever attempting to modify/delete (or reference) an existing object.<br>Field level constraints: must match pattern ^((?!;).)*$. (Note: Additional constraints might exist)
  interfaceFailureThreshold
    description:
      - <br>Field level constraints: cannot be null. (Note: Additional constraints might exist)
  interfaceFailureUnit
    description:
      - <br>Field level constraints: cannot be null. (Note: Additional constraints might exist)
  interfaceHoldTime
    description:
      - The interface hold time, which is how long to wait before failure assessment when a hello packet is not replied back. Interface hold time can be between 25000 and 75000 milliseconds in multiples of 1000. (5 to 75 seconds). Interface HoldTime should minimum five times the unit Interface PollTime. The timeUnit can be only MILLISECONDS or SECONDS <br>Field level constraints: cannot be null. (Note: Additional constraints might exist)
  interfacePollTime
    description:
      - The interface poll time, which is how often the hello packets are sent across interfaces. Interface poll time can be between 500 and 999 milliseconds. If higher should be in multiples of 1000 up to 15000 (1 second to 15 seconds). The timeUnit can be only MILLISECONDS or SECONDS<br>Field level constraints: cannot be null. (Note: Additional constraints might exist)
  limit
    description:
      - An integer representing the maximum amount of objects to return. If not specified, the maximum amount is 10
  name
    description:
      - A string that represents the name of the object
  offset
    description:
      - An integer representing the index of the first requested object. Index starts from 0. If not specified, the returned objects will start from index 0
  peerHoldTime
    description:
      - The peer hold time, which is how long to wait before making a failover assessment after not receiving a reply to a peer poll packet. Peer hold time is between 800 and 999 milliseconds, or 1000 and 45000 in multiples of 1000. You must enter a value that is at least 3 times the peerPollTimeInMsecs value. The timeUnit can be only MILLISECONDS or SECONDS<br>Field level constraints: cannot be null. (Note: Additional constraints might exist)
  peerPollTime
    description:
      - The peer poll time, which is how often to send hello packets across the failover link. Peer poll time is between 200 and 999 milliseconds, or 1000 and 15000 in multiples of 1000. The timeUnit can be only MILLISECONDS or SECONDS<br>Field level constraints: cannot be null. (Note: Additional constraints might exist)
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
- name: Fetch HAFailoverConfiguration with a given name
  ftd_ha_failover_configuration:
    operation: "getHAFailoverConfigurationByName"
    name: "Ansible HAFailoverConfiguration"
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


class HAFailoverConfigurationResource(object):

    def __init__(self, conn):
        self._conn = conn

    def editHAFailoverConfiguration(self, params):
        path_params = dict_subset(params, ['objId'])
        body_params = dict_subset(params, ['id', 'interfaceFailureThreshold', 'interfaceFailureUnit', 'interfaceHoldTime', 'interfacePollTime', 'name', 'peerHoldTime', 'peerPollTime', 'type', 'version'])

        return self._conn.send_request(
            url_path='/devices/default/ha/failoverconfigurations/{objId}',
            http_method='PUT',
            body_params=body_params,
            path_params=path_params,
        )

    def getHAFailoverConfiguration(self, params):
        path_params = dict_subset(params, ['objId'])

        return self._conn.send_request(
            url_path='/devices/default/ha/failoverconfigurations/{objId}',
            http_method='GET',
            path_params=path_params,
        )

    def getHAFailoverConfigurationList(self, params):
        query_params = dict_subset(params, ['filter', 'limit', 'offset', 'sort'])

        return self._conn.send_request(
            url_path='/devices/default/ha/failoverconfigurations',
            http_method='GET',
            query_params=query_params,
        )

    def getHAFailoverConfigurationByName(self, params):
        search_params = params.copy()
        search_params['filter'] = 'name:%s' % params['name']
        item_generator = iterate_over_pageable_resource(self.getHAFailoverConfigurationList, search_params)
        return next(item for item in item_generator if item['name'] == params['name'])

    def editHAFailoverConfigurationByName(self, params):
        existing_object = self.getHAFailoverConfigurationByName(params)
        params = copy_identity_properties(existing_object, params)
        return self.editHAFailoverConfiguration(params)


def main():
    fields = dict(
        operation=dict(type='str', choices=['editHAFailoverConfiguration', 'getHAFailoverConfiguration', 'getHAFailoverConfigurationList', 'getHAFailoverConfigurationByName', 'editHAFailoverConfigurationByName'], required=True),
        register_as=dict(type='str'),

        filter=dict(type='str'),
        id=dict(type='str'),
        interfaceFailureThreshold=dict(type='int'),
        interfaceFailureUnit=dict(type='str'),
        interfaceHoldTime=dict(type='str'),
        interfacePollTime=dict(type='str'),
        limit=dict(type='int'),
        name=dict(type='str'),
        objId=dict(type='str'),
        offset=dict(type='int'),
        peerHoldTime=dict(type='str'),
        peerPollTime=dict(type='str'),
        sort=dict(type='str'),
        type=dict(type='str'),
        version=dict(type='str'),
    )

    module = AnsibleModule(argument_spec=fields)
    params = module.params

    try:
        conn = Connection(module._socket_path)
        resource = HAFailoverConfigurationResource(conn)

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
