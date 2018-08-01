import re

INVALID_IDENTIFIER_SYMBOLS = r'[^a-zA-Z0-9_]'
IGNORED_FIELDS = ['id', 'version', 'isSystemDefined', 'links', 'eventLogAction', 'ruleAction', 'ruleId']


def dict_subset(dictionary, keys):
    return dict((k, dictionary[k]) for k in keys if dictionary[k])


def construct_ansible_facts(response, params):
    facts = dict()
    if response:
        response_body = response['items'] if 'items' in response else response
        if params.get('register_as'):
            facts[params['register_as']] = response_body
        elif 'name' in response_body and 'type' in response_body:
            object_name = re.sub(INVALID_IDENTIFIER_SYMBOLS, '_', response_body['name'].lower())
            fact_name = '%s_%s' % (response_body['type'], object_name)
            facts[fact_name] = response_body
    return facts


def copy_identity_properties(source_obj, dest_obj):
    dest_obj['objId'] = source_obj['id']
    dest_obj['id'] = source_obj['id']
    if 'version' in source_obj:
        dest_obj['version'] = source_obj['version']
    if 'ruleId' in source_obj:
        dest_obj['ruleId'] = source_obj['ruleId']
    return dest_obj


def is_object_ref(d):
    if type(d) is not dict:
        return False

    has_id = 'id' in d.keys() and d['id']
    has_type = 'type' in d.keys() and d['type']
    return has_id and has_type


def equal_object_refs(d1, d2):
    have_equal_ids = d1['id'] == d2['id']
    have_equal_types = d1['type'] == d2['type']
    return have_equal_ids and have_equal_types


def equal_objects(dict1, dict2):
    def _equal_lists(l1, l2):
        import json
        with open('/tmp/test1', 'wt') as f1:
            f1.write(json.dumps(l1))
        with open('/tmp/test2', 'wt') as f2:
            f2.write(json.dumps(l2))

        if len(l1) != len(l2):
            return False

        for v1, v2 in zip(l1, l2):
            if type(v1) != type(v2):
                return False

            if is_object_ref(v1) and is_object_ref(v2):
                equal_vs = equal_object_refs(v1, v2)
            else:
                equal_vs = v1 == v2

            if not equal_vs:
                return False

        return True

    if type(dict1) is not dict or type(dict2) is not dict:
        raise ValueError("Arguments must be dictionaries")

    dict1 = dict((k, dict1[k]) for k in dict1.keys() if k not in IGNORED_FIELDS and dict1[k])
    dict2 = dict((k, dict2[k]) for k in dict2.keys() if k not in IGNORED_FIELDS and dict2[k])

    if len(dict1) != len(dict2):
        return False

    for key, value1 in dict1.items():
        if key not in dict2:
            return False

        value2 = dict2[key]

        if type(value1) != type(value2):
            return False

        if type(value1) == list:
            equal_values = _equal_lists(value1, value2)
        elif is_object_ref(value1) and is_object_ref(value2):
            equal_values = equal_object_refs(value1, value2)
        else:
            equal_values = value1 == value2

        if not equal_values:
            return False

    return True
