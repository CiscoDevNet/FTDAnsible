def dict_subset(dictionary, keys):
    return {k: dictionary[k] for k in keys if dictionary[k]}


def construct_module_result(response, params):
    def register_return_fact(facts):
        if 'register_as' in params and response:
            response_body = response['items'] if 'items' in response else response
            facts[params['register_as']] = response_body
        return facts

    def refresh_token_facts(facts):
        facts['access_token'] = str(params['access_token'])
        facts['refresh_token'] = str(params['refresh_token'])
        return facts

    result = dict(changed=True, response=response, ansible_facts=dict())
    result['ansible_facts'] = register_return_fact(result['ansible_facts'])
    result['ansible_facts'] = refresh_token_facts(result['ansible_facts'])
    return result
