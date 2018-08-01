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
    has_id = 'id' in d.keys() and d['id']
    has_type = 'type' in d.keys() and d['type']
    return has_id and has_type


def equal_object_refs(d1, d2):
    have_equal_ids = d1['id'] == d2['id']
    have_equal_types = d1['type'] == d2['type']
    return have_equal_ids and have_equal_types


def equal_lists(l1, l2):
    if len(l1) != len(l2):
        return False

    for v1, v2 in zip(l1, l2):
        if type(v1) != type(v2):
            return False
        value_type = type(v1)

        if value_type == dict and is_object_ref(v1) and is_object_ref(v2):
            equal_values = equal_object_refs(v1, v2)
        else:
            equal_values = v1 == v2

        if not equal_values:
            return False

    return True


def equal_objects(d1, d2):
    d1 = dict((k, d1[k]) for k in d1.keys() if k not in IGNORED_FIELDS and d1[k])
    d2 = dict((k, d2[k]) for k in d2.keys() if k not in IGNORED_FIELDS and d2[k])

    if len(d1) != len(d2):
        return False

    for key, v1 in d1.items():
        if key not in d2:
            return False

        v2 = d2[key]

        if type(v1) != type(v2):
            return False
        value_type = type(v1)

        if value_type == list:
            equal_values = equal_lists(v1, v2)
        elif value_type == dict and is_object_ref(v1) and is_object_ref(v2):
            equal_values = equal_object_refs(v1, v2)
        else:
            equal_values = v1 == v2

        if not equal_values:
            return False

    return True
