IGNORED_FIELDS = ['id', 'version', 'isSystemDefined', 'links']


def equal_objects(dict1, dict2):
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

        equal_values = value1 == value2 if type(value1) != dict else equal_objects(value1, value2)
        if not equal_values:
            return False

    return True
