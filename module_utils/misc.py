import re

INVALID_IDENTIFIER_SYMBOLS = r'[^a-zA-Z0-9_]'


def camel_to_snake(text):
    test_with_underscores = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', test_with_underscores).lower()


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

    def refresh_token_facts(facts):
        facts['access_token'] = str(params['access_token'])
        facts['refresh_token'] = str(params['refresh_token'])
        return facts

    result = dict(changed=True, response=response, ansible_facts=dict())
    result['ansible_facts'] = register_return_fact(result['ansible_facts'])
    result['ansible_facts'] = refresh_token_facts(result['ansible_facts'])
    return result


def copy_identity_properties(source_obj, dest_obj):
    dest_obj['objId'] = source_obj['id']
    dest_obj['id'] = source_obj['id']
    if 'version' in source_obj:
        dest_obj['version'] = source_obj['version']
    if 'ruleId' in source_obj:
        dest_obj['ruleId'] = source_obj['ruleId']
    return dest_obj
