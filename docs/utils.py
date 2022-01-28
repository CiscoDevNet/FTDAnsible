from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible_collections.cisco.ftdansible.plugins.module_utils.common import HTTPMethod, IDENTITY_PROPERTIES


def filter_data_params(op_name, op_method, data_params):
    blocked_properties = []

    if op_name.startswith('add') and op_method == HTTPMethod.POST:
        blocked_properties = IDENTITY_PROPERTIES

    return {k: v for k, v in data_params.items() if k not in blocked_properties}
