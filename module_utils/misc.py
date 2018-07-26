import re

INVALID_IDENTIFIER_SYMBOLS = r'[^a-zA-Z0-9_]'
IGNORED_FIELDS = ['id', 'version', 'isSystemDefined', 'links']


def dict_subset(dictionary, keys):
    return dict((k, dictionary[k]) for k in keys if dictionary[k])


def construct_module_result(response, params):
    def register_return_fact(facts):
        if response:
            response_body = response['items'] if 'items' in response else response
            if params.get('register_as'):
                facts[params['register_as']] = response_body
            elif 'name' in response_body and 'type' in response_body:
                object_name = re.sub(INVALID_IDENTIFIER_SYMBOLS, '_', response_body['name'].lower())
                fact_name = '%s_%s' % (response_body['type'], object_name)
                facts[fact_name] = response_body
        return facts

    result = dict(changed=True, response=response, ansible_facts=dict())
    result['ansible_facts'] = register_return_fact(result['ansible_facts'])
    return result


def copy_identity_properties(source_obj, dest_obj):
    dest_obj['objId'] = source_obj['id']
    dest_obj['id'] = source_obj['id']
    if 'version' in source_obj:
        dest_obj['version'] = source_obj['version']
    if 'ruleId' in source_obj:
        dest_obj['ruleId'] = source_obj['ruleId']
    return dest_obj


def equal_dicts(dict1, dict2):
    if type(dict1) is not dict or type(dict2) is not dict:
        raise ValueError("Arguments must be dictionaries")

    dict1 = dict((k, dict1[k]) for k in dict1.keys() if k not in IGNORED_FIELDS)
    dict2 = dict((k, dict2[k]) for k in dict2.keys() if k not in IGNORED_FIELDS)

    if len(dict1) != len(dict2):
        return False

    for key, value1 in dict1.items():
        if key not in dict2:
            return False

        value2 = dict2[key]

        if type(value1) != type(value2):
            return False

        equal_values = value1 == value2 if type(value1) != dict else equal_dicts(value1, value2)
        if not equal_values:
            return False

    return True
