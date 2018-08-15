import os
import unittest

try:
    from ansible.module_utils.fdm_swagger_client import FdmSwaggerValidator
except ModuleNotFoundError:
    from module_utils.fdm_swagger_client import FdmSwaggerValidator
DIR_PATH = os.path.dirname(os.path.realpath(__file__))
TEST_DATA_FOLDER = os.path.join(DIR_PATH, 'test_data')

mock_data = {
    'models': {
        'ReferenceModel': {'type': 'object', 'required': ['id', 'type'],
                           'properties': {'id': {'type': 'string'}, 'type': {'type': 'string'},
                                          'version': {'type': 'string'}, 'name': {'type': 'string'}}},
        'FQDNDNSResolution': {'type': 'string', 'enum': ['IPV4_ONLY', 'IPV6_ONLY', 'IPV4_AND_IPV6']},
        'NetworkObjectType': {'type': 'string', 'enum': ['HOST', 'NETWORK', 'IPRANGE', 'FQDN']},
        'NetworkObject': {'type': 'object',
                          'properties': {'version': {'type': 'string'},
                                         'name': {'type': 'string'},
                                         'description': {'type': 'string'},
                                         'subType': {'type': 'object',
                                                     '$ref': '#/definitions/NetworkObjectType'},
                                         'value': {'type': 'string'},
                                         'isSystemDefined': {'type': 'boolean'},
                                         'dnsResolution': {'type': 'object',
                                                           '$ref': '#/definitions/FQDNDNSResolution'},
                                         'objects': {'type': 'array',
                                                     'items': {'type': 'object',
                                                               '$ref': '#/definitions/ReferenceModel'}},
                                         'id': {'type': 'string'},
                                         'type': {'type': 'string',
                                                  'default': 'networkobject'}},
                          'required': ['subType', 'type', 'value']}
    },
    'operations': {
        'getNetworkObjectList': {
            'method': 'get',
            'url': '/api/fdm/v2/object/networks',
            'modelName': 'NetworkObject',
            'parameters': {
                'path': {
                    'objId': {
                        'required': True,
                        'type': "string"
                    }
                },
                'query': {
                    'offset': {
                        'required': False,
                        'type': 'integer'
                    },
                    'limit': {
                        'required': True,
                        'type': 'integer'
                    },
                    'sort': {
                        'required': False,
                        'type': 'string'
                    },
                    'filter': {
                        'required': False,
                        'type': 'string'
                    }
                }
            }
        }
    }
}

nested_mock_data1 = {
    'models': {
        'model1': {
            'type': 'object',
            'properties': {
                'f_string': {'type': 'string'},
                'f_number': {'type': 'number'},
                'f_boolean': {'type': 'boolean'},
                'f_integer': {'type': 'integer'}
            },
            'required': ['f_string']
        },
        'TestModel': {
            'type': 'object',
            'properties': {
                'nested_model': {'type': 'object',
                                 '$ref': '#/definitions/model1'},
                'f_integer': {'type': 'integer'}
            },
            'required': ['nested_model']
        }
    },
    'operations': {
        'getdata': {
            'modelName': 'TestModel'
        }
    }
}


class TestFdmSwaggerValidator(unittest.TestCase):

    def test_path_params__(self):
        assert False

    def test_query_params__(self):
        assert False

    def test_errors_for_required_fields(self):
        data = {
            'name': 'test'
        }
        valid, rez = FdmSwaggerValidator(mock_data).validate_data('getNetworkObjectList', data)
        assert not valid
        assert {
                   'status': 'invalid',
                   'required': ['subType', 'type', 'value'],
                   'invalid_type': []
               } == rez

    def test_errors_if_no_data_was_passed(self):
        data = {}
        valid, rez = FdmSwaggerValidator(mock_data).validate_data('getNetworkObjectList', data)
        assert not valid
        assert {
                   'status': 'invalid',
                   'required': ['subType', 'type', 'value'],
                   'invalid_type': []
               } == rez

    def test_errors_if_one_required_field_is_empty(self):
        data = {
            'subType': 'NETWORK',
            'value': '1.1.1.1'
        }
        valid, rez = FdmSwaggerValidator(mock_data).validate_data('getNetworkObjectList', data)
        assert not valid
        assert {
                   'status': 'invalid',
                   'required': ['type'],
                   'invalid_type': []
               } == rez

    def test_types_of_required_fields_are_incorrect(self):
        data = {
            'subType': True,
            'type': 1,
            'value': False
        }
        valid, rez = FdmSwaggerValidator(mock_data).validate_data('getNetworkObjectList', data)
        assert not valid
        assert {
                   'status': 'invalid',
                   'required': [],
                   'invalid_type': [
                       {
                           'path': 'subType',
                           'expected_type': 'enum',
                           'actually_value': True
                       },
                       {
                           'path': 'value',
                           'expected_type': 'string',
                           'actually_value': False
                       },
                       {
                           'path': 'type',
                           'expected_type': 'string',
                           'actually_value': 1
                       }
                   ]
               } == rez
        data = {
            'subType': {},
            'type': [],
            'value': {}
        }
        valid, rez = FdmSwaggerValidator(mock_data).validate_data('getNetworkObjectList', data)
        assert not valid
        assert {
                   'status': 'invalid',
                   'required': [],
                   'invalid_type': [
                       {
                           'path': 'subType',
                           'expected_type': 'enum',
                           'actually_value': {}
                       },
                       {
                           'path': 'value',
                           'expected_type': 'string',
                           'actually_value': {}
                       },
                       {
                           'path': 'type',
                           'expected_type': 'string',
                           'actually_value': []
                       }
                   ]
               } == rez

    def test_pass_only_required_fields(self):
        data = {
            'subType': 'NETWORK',
            'type': 'networkobject',
            'value': '1.1.1.1'
        }
        valid, rez = FdmSwaggerValidator(mock_data).validate_data('getNetworkObjectList', data)
        assert valid
        assert rez is None

    def test_pass_all_fields_with_correct_data(self):
        data = {
            'id': 'id-di',
            'version': 'v',
            'name': 'test_name',
            'subType': 'NETWORK',
            'type': 'networkobject',
            'value': '1.1.1.1',
            'description': 'des',
            'isSystemDefined': False,
            'dnsResolution': 'IPV4_ONLY',
            'objects': [{
                'type': 'port',
                'id': 'fs-sf'
            }]
        }
        valid, rez = FdmSwaggerValidator(mock_data).validate_data('getNetworkObjectList', data)
        assert valid
        assert rez is None

    def test_array_data_is_not_correct(self):
        data = {
            'name': 'test_name',
            'subType': 'NETWORK',
            'type': 'networkobject',
            'value': '1.1.1.1',
            'objects': [
                {
                    'id': 'fs-sf'
                },
                {
                    'type': 'type'
                },
                {},
                {
                    'id': 1,
                    'type': True
                },
                [],
                'test'
            ]
        }
        valid, rez = FdmSwaggerValidator(mock_data).validate_data('getNetworkObjectList', data)
        assert not valid
        assert {
                   'status': 'invalid',
                   'required': ['objects[0].type', 'objects[1].id', 'objects[2].id', 'objects[2].type'],
                   'invalid_type': [
                       {
                           'path': 'objects[3].id',
                           'expected_type': 'string',
                           'actually_value': 1
                       },
                       {
                           'path': 'objects[3].type',
                           'expected_type': 'string',
                           'actually_value': True
                       },
                       {
                           'path': 'objects[4]',
                           'expected_type': 'object',
                           'actually_value': []
                       },
                       {
                           'path': 'objects[5]',
                           'expected_type': 'object',
                           'actually_value': 'test'
                       }
                   ]
               } == rez

    def test_simple_types(self):
        local_mock_data = {
            'models': {
                'TestModel': {
                    'type': 'object',
                    'properties': {
                        'f_string': {'type': 'string'},
                        'f_number': {'type': 'number'},
                        'f_boolean': {'type': 'boolean'},
                        'f_integer': {'type': 'integer'}
                    },
                    'required': []
                }
            },
            'operations': {
                'getdata': {
                    'modelName': 'TestModel'
                }
            }
        }
        valid_data = {
            "f_string": "test",
            "f_number": 2.2,
            "f_boolean": False,
            "f_integer": 1
        }

        valid, rez = FdmSwaggerValidator(local_mock_data).validate_data('getdata', valid_data)
        assert valid
        assert rez is None

        valid_data = {
            "f_string": "",
            "f_number": 0,
            "f_boolean": True,
            "f_integer": 0
        }

        valid, rez = FdmSwaggerValidator(local_mock_data).validate_data('getdata', valid_data)
        assert valid
        assert rez is None

        valid_data = {
            "f_string": "0",
            "f_number": 100,
            "f_boolean": True,
            "f_integer": 2
        }

        valid, rez = FdmSwaggerValidator(local_mock_data).validate_data('getdata', valid_data)
        assert valid
        assert rez is None

    def test_invalid_simple_types(self):
        local_mock_data = {
            'models': {
                'TestModel': {
                    'type': 'object',
                    'properties': {
                        'f_string': {'type': 'string'},
                        'f_number': {'type': 'number'},
                        'f_boolean': {'type': 'boolean'},
                        'f_integer': {'type': 'integer'}
                    },
                    'required': []
                }
            },
            'operations': {
                'getdata': {
                    'modelName': 'TestModel'
                }
            }
        }
        invalid_data = {
            "f_string": True,
            "f_number": True,
            "f_boolean": 1,
            "f_integer": True
        }

        valid, rez = FdmSwaggerValidator(local_mock_data).validate_data('getdata', invalid_data)
        assert not valid
        assert {
                   'status': 'invalid',
                   'required': [],
                   'invalid_type': [
                       {
                           'path': 'f_string',
                           'expected_type': 'string',
                           'actually_value': True
                       },
                       {
                           'path': 'f_number',
                           'expected_type': 'number',
                           'actually_value': True
                       },
                       {
                           'path': 'f_boolean',
                           'expected_type': 'boolean',
                           'actually_value': 1
                       },
                       {
                           'path': 'f_integer',
                           'expected_type': 'integer',
                           'actually_value': True
                       }
                   ]
               } == rez

        invalid_data = {
            "f_string": 1,
            "f_number": False,
            "f_boolean": 0,
            "f_integer": "test"
        }

        valid, rez = FdmSwaggerValidator(local_mock_data).validate_data('getdata', invalid_data)
        assert not valid
        assert {
                   'status': 'invalid',
                   'required': [],
                   'invalid_type': [
                       {
                           'path': 'f_string',
                           'expected_type': 'string',
                           'actually_value': 1
                       },
                       {
                           'path': 'f_number',
                           'expected_type': 'number',
                           'actually_value': False
                       },
                       {
                           'path': 'f_boolean',
                           'expected_type': 'boolean',
                           'actually_value': 0
                       },
                       {
                           'path': 'f_integer',
                           'expected_type': 'integer',
                           'actually_value': "test"
                       }
                   ]
               } == rez

        invalid_data = {
            "f_string": False,
            "f_number": "1",
            "f_boolean": "",
            "f_integer": 1.2
        }

        valid, rez = FdmSwaggerValidator(local_mock_data).validate_data('getdata', invalid_data)
        assert not valid
        assert {
                   'status': 'invalid',
                   'required': [],
                   'invalid_type': [
                       {
                           'path': 'f_string',
                           'expected_type': 'string',
                           'actually_value': False
                       },
                       {
                           'path': 'f_number',
                           'expected_type': 'number',
                           'actually_value': "1"
                       },
                       {
                           'path': 'f_boolean',
                           'expected_type': 'boolean',
                           'actually_value': ""
                       },
                       {
                           'path': 'f_integer',
                           'expected_type': 'integer',
                           'actually_value': 1.2
                       }
                   ]
               } == rez

    def test_nested_required_fields(self):
        valid_data = {
            'nested_model': {
                'f_string': "test"
            }
        }

        valid, rez = FdmSwaggerValidator(nested_mock_data1).validate_data('getdata', valid_data)
        assert valid
        assert rez is None

    def test_invalid_nested_required_fields(self):
        invalid_data = {
            'f_integer': 2
        }

        valid, rez = FdmSwaggerValidator(nested_mock_data1).validate_data('getdata', invalid_data)
        assert not valid
        assert {
                   'status': 'invalid',
                   'required': ['nested_model'],
                   'invalid_type': []
               } == rez

        invalid_data = {
            'nested_model': {
                'f_number': 1.2
            }
        }

        valid, rez = FdmSwaggerValidator(nested_mock_data1).validate_data('getdata', invalid_data)
        assert not valid
        assert {
                   'status': 'invalid',
                   'required': ['nested_model.f_string'],
                   'invalid_type': []
               } == rez

    def test_invalid_type_in_nested_fields(self):
        invalid_data = {
            'nested_model': {
                "f_string": 1,
                "f_number": "ds",
                "f_boolean": 1.3,
                "f_integer": True
            }
        }

        valid, rez = FdmSwaggerValidator(nested_mock_data1).validate_data('getdata', invalid_data)
        assert not valid
        assert {
                   'status': 'invalid',
                   'required': [],
                   'invalid_type': [
                       {
                           'path': 'nested_model.f_string',
                           'expected_type': 'string',
                           'actually_value': 1
                       },
                       {
                           'path': 'nested_model.f_number',
                           'expected_type': 'number',
                           'actually_value': "ds"
                       },
                       {
                           'path': 'nested_model.f_boolean',
                           'expected_type': 'boolean',
                           'actually_value': 1.3
                       },
                       {
                           'path': 'nested_model.f_integer',
                           'expected_type': 'integer',
                           'actually_value': True
                       }
                   ]

               } == rez

    def test_few_levels_nested_fields(self):
        local_mock_data = {
            'models': {
                'Model2': {
                    'type': 'object',
                    'required': ['ms', 'ts'],
                    'properties': {
                        'ms': {'type': 'array',
                               'items': {
                                   'type': 'object',
                                   '$ref': '#/definitions/ReferenceModel'}},
                        'ts': {'type': 'array',
                               'items': {
                                   'type': 'object',
                                   '$ref': '#/definitions/ReferenceModel'}}
                    }
                },
                'NetworkObjectType': {'type': 'string', 'enum': ['HOST', 'NETWORK', 'IPRANGE', 'FQDN']},
                'Fragment': {'type': 'object',
                             'required': ['type', 'objects', 'subType', 'object'],
                             'properties': {
                                 'objects': {'type': 'array',
                                             'items': {
                                                 'type': 'object',
                                                 '$ref': '#/definitions/ReferenceModel'}},
                                 'object': {'type': 'object',
                                            '$ref': '#/definitions/Model2'},
                                 'subType': {'type': 'object',
                                             '$ref': '#/definitions/NetworkObjectType'},
                                 'type': {'type': 'string'},
                                 'value': {'type': 'number'},
                                 'name': {'type': 'string'}}},
                'ReferenceModel': {'type': 'object', 'required': ['id', 'type'],
                                   'properties': {
                                       'id': {'type': 'string'},
                                       'type': {'type': 'string'},
                                       'version': {'type': 'string'},
                                       'name': {'type': 'string'}}},
                'model1': {
                    'type': 'object',
                    'properties': {
                        'f_string': {'type': 'string'},
                        'f_number': {'type': 'number'},
                        'f_boolean': {'type': 'boolean'},
                        'f_integer': {'type': 'integer'},
                        'objects': {'type': 'array',
                                    'items': {
                                        'type': 'object',
                                        '$ref': '#/definitions/ReferenceModel'}},
                        'fragments': {'type': 'array',
                                      'items': {
                                          'type': 'object',
                                          '$ref': '#/definitions/Fragment'}}
                    },
                    'required': ['f_string', 'objects', 'fragments']
                },
                'TestModel': {
                    'type': 'object',
                    'properties': {
                        'nested_model': {'type': 'object',
                                         '$ref': '#/definitions/model1'},
                        'f_integer': {'type': 'integer'}
                    },
                    'required': ['nested_model']
                }
            },
            'operations': {
                'getdata': {
                    'modelName': 'TestModel'
                }
            }
        }

        valid_data = {
            "nested_model": {
                'objects': [{
                    'type': 't1',
                    'id': 'id1'
                }],
                'fragments': [{
                    'type': "test",
                    'subType': 'NETWORK',
                    'object': {
                        'ts': [],
                        'ms': [{
                            'type': "tt",
                            'id': 'id'
                        }]
                    },
                    'objects': [{
                        'type': 't',
                        'id': 'id'
                    }]
                }],
                'f_string': '1'
            }
        }

        valid, rez = FdmSwaggerValidator(local_mock_data).validate_data('getdata', valid_data)
        assert valid
        assert rez is None

        valid_data = {
            "nested_model": {
                'objects': [{
                    'type': 't1',
                    'id': 'id1'
                }],
                'fragments': [{
                    'type': "test",
                    'subType': 'NETWORK',
                    'object': {
                        'ms': {}
                    },
                    'objects': [{
                        'type': 't',
                        'id': 'id'
                    }]
                }],
                'f_string': '1'
            }
        }

        valid, rez = FdmSwaggerValidator(local_mock_data).validate_data('getdata', valid_data)
        assert not valid
        assert {
                   'required': ['nested_model.fragments[0].object.ts'],
                   'invalid_type': [{
                       'path': 'nested_model.fragments[0].object.ms',
                       'expected_type': 'array',
                       'actually_value': {}
                   }],
                   'status': 'invalid'} == rez

        valid_data = {
            "nested_model": {
                'objects': [{
                    'type': 't1',
                    'id': 'id1'
                }],
                'fragments': [{
                    'type': "test",
                    'subType': 'NETWORK',
                    'object': [],
                    'objects': {}
                }],
                'f_string': '1'
            }
        }

        valid, rez = FdmSwaggerValidator(local_mock_data).validate_data('getdata', valid_data)
        assert not valid
        assert {
                   'required': [],
                   'invalid_type': [
                       {
                           'path': 'nested_model.fragments[0].objects',
                           'expected_type': 'array',
                           'actually_value': {}
                       },
                       {
                           'path': 'nested_model.fragments[0].object',
                           'expected_type': 'object',
                           'actually_value': []}
                   ], 'status': 'invalid'} == rez
