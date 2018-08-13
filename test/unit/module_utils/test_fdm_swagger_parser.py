import copy
import json
import os
import unittest

try:
    from ansible.module_utils.fdm_swagger_client import FdmSwaggerParser
    from ansible.module_utils.http import HTTPMethod
except ModuleNotFoundError:
    from module_utils.fdm_swagger_client import FdmSwaggerParser
    from module_utils.http import HTTPMethod

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
TEST_DATA_FOLDER = os.path.join(DIR_PATH, 'test_data')
base = {
    'basePath': "/api/fdm/v2",
    'definitions': {},
    'paths': {}
}


def _get_objects(base_object, key_names):
    return {_key: base_object[_key] for _key in key_names}


class TestFdmSwaggerParser(unittest.TestCase):
    def setUp(self):
        self.init_mock_data()

    def init_mock_data(self):
        with open(os.path.join(TEST_DATA_FOLDER, 'ngfw.json')) as f:
            self.base_data = json.load(f)
            self._data = copy.deepcopy(base)

    def test_simple_object(self):
        self._data['definitions'] = _get_objects(self.base_data['definitions'],
                                                 ['NetworkObject', 'NetworkObjectWrapper'])

        self._data['paths'] = _get_objects(self.base_data['paths'],
                                           ['/object/networks', '/object/networks/{objId}'])

        self.fdm_data = FdmSwaggerParser().parse_spec(self._data)

        expected_operations = {
            'getNetworkObjectList': {
                'method': HTTPMethod.GET,
                'url': '/api/fdm/v2/object/networks',
                'modelName': 'NetworkObject',
                'parameters': {
                    'path': {},
                    'query': {
                        'offset': {
                            'required': False,
                            'type': 'integer'
                        },
                        'limit': {
                            'required': False,
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
            },
            'addNetworkObject': {
                'method': HTTPMethod.POST,
                'url': '/api/fdm/v2/object/networks',
                'modelName': 'NetworkObject',
                'parameters': {'path': {},
                               'query': {}}
            },
            'getNetworkObject': {
                'method': HTTPMethod.GET,
                'url': '/api/fdm/v2/object/networks/{objId}',
                'modelName': 'NetworkObject',
                'parameters': {
                    'path': {
                        'objId': {
                            'required': True,
                            'type': "string"
                        }
                    },
                    'query': {}
                }
            },
            'editNetworkObject': {
                'method': HTTPMethod.PUT,
                'url': '/api/fdm/v2/object/networks/{objId}',
                'modelName': 'NetworkObject',
                'parameters': {
                    'path': {
                        'objId': {
                            'required': True,
                            'type': "string"
                        }
                    },
                    'query': {}
                }
            },
            'deleteNetworkObject': {
                'method': HTTPMethod.DELETE,
                'url': '/api/fdm/v2/object/networks/{objId}',
                'modelName': None,
                'parameters': {
                    'path': {
                        'objId': {
                            'required': True,
                            'type': "string"
                        }
                    },
                    'query': {}
                }
            }
        }
        self.assertEquals(['NetworkObject', 'NetworkObjectWrapper'], list(self.fdm_data['models'].keys()))
        self.assertEquals(expected_operations, self.fdm_data['operations'])

    def test_parse_all_data(self):
        self._data['definitions'] = self.base_data['definitions']

        self._data['paths'] = self.base_data['paths']

        self.fdm_data = FdmSwaggerParser().parse_spec(self._data)
        operations = self.fdm_data['operations']
        without_model_name = []
        expected_operations_counter = 0
        for key in self._data['paths']:
            operation = self._data['paths'][key]
            for _ in operation:
                expected_operations_counter += 1

        for key in operations:
            operation = operations[key]
            if not operation['modelName'] and (operation['method'] != HTTPMethod.DELETE):
                without_model_name.append(operation['url'])

            if operation['modelName'] == '_File' and 'download' not in operation['url']:
                self.fail('File type can be defined for download operation only')

        self.assertEquals(['/api/fdm/v2/action/upgrade'], without_model_name)
        self.assertEquals(expected_operations_counter, len(operations))
