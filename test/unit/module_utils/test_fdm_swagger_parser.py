import copy
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
    'definitions': {"NetworkObject": {"type": "object",
                                      "properties": {"version": {"type": "string"}, "name": {"type": "string"},
                                                     "description": {"type": "string"},
                                                     "subType": {"type": "object",
                                                                 "$ref": "#/definitions/NetworkObjectType"},
                                                     "value": {"type": "string"},
                                                     "isSystemDefined": {"type": "boolean"},
                                                     "dnsResolution": {"type": "object",
                                                                       "$ref": "#/definitions/FQDNDNSResolution"},
                                                     "id": {"type": "string"},
                                                     "type": {"type": "string", "default": "networkobject"}},
                                      "required": ["subType", "type", "value"]},
                    "NetworkObjectWrapper": {
                        "allOf": [{"$ref": "#/definitions/NetworkObject"}, {"$ref": "#/definitions/LinksWrapper"}]}
                    },
    'paths': {
        "/object/networks": {
            "get": {"tags": ["NetworkObject"], "operationId": "getNetworkObjectList",
                    "responses": {"200": {"description": "", "schema": {"type": "object",
                                                                        "title": "NetworkObjectList",
                                                                        "properties": {"items": {
                                                                            "type": "array",
                                                                            "items": {
                                                                                "$ref": "#/definitions/NetworkObjectWrapper"}},
                                                                            "paging": {
                                                                                "$ref": "#/definitions/Paging"}},
                                                                        "required": ["items",
                                                                                     "paging"]}}},
                    "parameters": [
                        {"name": "offset", "in": "query", "required": False, "type": "integer"},
                        {"name": "limit", "in": "query", "required": False, "type": "integer"},
                        {"name": "sort", "in": "query", "required": False, "type": "string"},
                        {"name": "filter", "in": "query", "required": False, "type": "string"}]},
            "post": {"tags": ["NetworkObject"], "operationId": "addNetworkObject",
                     "responses": {
                         "200": {"description": "",
                                 "schema": {"type": "object",
                                            "$ref": "#/definitions/NetworkObjectWrapper"}},
                         "422": {"description": "",
                                 "schema": {"type": "object", "$ref": "#/definitions/ErrorWrapper"}}
                     },
                     "parameters": [{"in": "body", "name": "body",
                                     "required": True,
                                     "schema": {"$ref": "#/definitions/NetworkObject"}}]}
        },
        "/object/networks/{objId}": {
            "get": {"tags": ["NetworkObject"], "operationId": "getNetworkObject",
                    "responses": {"200": {"description": "",
                                          "schema": {"type": "object",
                                                     "$ref": "#/definitions/NetworkObjectWrapper"}},
                                  "404": {"description": "",
                                          "schema": {"type": "object",
                                                     "$ref": "#/definitions/ErrorWrapper"}}},
                    "parameters": [{"name": "objId", "in": "path", "required": True,
                                    "type": "string"}]},

            "put": {"tags": ["NetworkObject"], "operationId": "editNetworkObject",
                    "responses": {"200": {"description": "",
                                          "schema": {"type": "object",
                                                     "$ref": "#/definitions/NetworkObjectWrapper"}},
                                  "422": {"description": "",
                                          "schema": {"type": "object",
                                                     "$ref": "#/definitions/ErrorWrapper"}}},
                    "parameters": [{"name": "objId", "in": "path", "required": True,
                                    "type": "string"},
                                   {"in": "body", "name": "body", "required": True,
                                    "schema": {"$ref": "#/definitions/NetworkObject"}}]},
            "delete": {"tags": ["NetworkObject"], "operationId": "deleteNetworkObject",
                       "responses": {"204": {"description": ""},
                                     "422": {"description": "",
                                             "schema": {"type": "object",
                                                        "$ref": "#/definitions/ErrorWrapper"}}},
                       "parameters": [{"name": "objId", "in": "path", "required": True,
                                       "type": "string"}]}}}
}


def _get_objects(base_object, key_names):
    return {_key: base_object[_key] for _key in key_names}


class TestFdmSwaggerParser(unittest.TestCase):

    def test_simple_object(self):
        self._data = copy.deepcopy(base)

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
        assert ['NetworkObject', 'NetworkObjectWrapper'] == list(self.fdm_data['models'].keys())
        assert expected_operations == self.fdm_data['operations']
