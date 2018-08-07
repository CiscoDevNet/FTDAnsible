import copy
import json
import os
import pprint
import unittest

from hamcrest import equal_to, assert_that

from module_utils.fdm_swagger_client import FdmSwaggerClient

pp = pprint.PrettyPrinter(width=41, compact=True)

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
TEST_DATA_FOLDER = os.path.join(DIR_PATH, 'test_data')
base = {
    'basePath': "/api/fdm/v2",
    'definitions': {},
    'paths': {}
}


def _get_objects(base_object, key_names):
    return {_key: base_object[_key] for _key in key_names}


class TestFdmSwaggerClient(unittest.TestCase):
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

        self.fdm_swagger_client = FdmSwaggerClient(spec=self._data)

        expected_operations = {
            'getNetworkObjectList': {
                'method': 'get',
                'url': '/object/networks',
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
                'method': 'post',
                'url': '/object/networks',
                'modelName': 'NetworkObject',
                'parameters': {'path': {},
                               'query': {}}
            },
            'getNetworkObject': {
                'method': 'get',
                'url': '/object/networks/{objId}',
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
                'method': 'put',
                'url': '/object/networks/{objId}',
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
                'method': 'delete',
                'url': '/object/networks/{objId}',
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
        assert_that(['NetworkObject', 'NetworkObjectWrapper'],
                    equal_to(list(self.fdm_swagger_client.get_models().keys())))
        # test_prop = 'deleteNetworkObject'
        # pp.pprint(expected_operations[test_prop])
        # pp.pprint(self.fdm_swagger_client.get_operations()[test_prop])
        assert_that(expected_operations, equal_to(self.fdm_swagger_client.get_operations()))
