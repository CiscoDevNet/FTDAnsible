import copy
import json
import os
import time
import unittest

import requests
from hamcrest import equal_to, assert_that

try:
    from ansible.module_utils.fdm_swagger_client import FdmSwaggerClient
except ModuleNotFoundError:
    from module_utils.fdm_swagger_client import FdmSwaggerClient

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
TEST_DATA_FOLDER = os.path.join(DIR_PATH, 'test_data')
base = {
    'basePath': "/api/fdm/v2",
    'definitions': {},
    'paths': {}
}


def _get_objects(base_object, key_names):
    return {_key: base_object[_key] for _key in key_names}


class FtdConnection(object):
    HOST = 'http://localhost:4200'

    def send_request(self, url_path):
        response = requests.get(self.HOST + url_path)
        return json.loads(response.text)


class TestFdmSwaggerClient(unittest.TestCase):
    def setUp(self):
        self.init_mock_data()

    def init_mock_data(self):
        with open(os.path.join(TEST_DATA_FOLDER, 'ngfw.json')) as f:
            self.base_data = json.load(f)
            self._data = copy.deepcopy(base)

    def test_parse_all_data(self):
        swagger_client = FdmSwaggerClient(conn=FtdConnection())

        operations = swagger_client.get_operations()
        without_model_name = []
        expected_operations_counter = 0
        for key in self._data['paths']:
            operation = self._data['paths'][key]
            for _ in operation:
                expected_operations_counter += 1

        for key in operations:
            operation = operations[key]
            if not operation['modelName'] and (operation['method'] != 'delete'):
                without_model_name.append(operation['url'])

            if operation['modelName'] == '_File' and 'download' not in operation['url']:
                assert_that(False)
        assert_that(['/api/fdm/v2/action/upgrade'], equal_to(without_model_name))
        assert_that(equal_to(len(list(operations.items()))), expected_operations_counter)

    def test_data_should_be_cached(self):
        response = {
            'basePath': "/api/fdm/v2",
            'definitions': {
                'TestModel': {}
            },
            'paths': {
                'testPath': {}
            }
        }

        class MockConnection:
            def send_request(self, url_path):
                return copy.deepcopy(response)

        dir_path = os.path.dirname(os.path.realpath(__file__))
        swagger_client = FdmSwaggerClient(conn=MockConnection(),
                                          cache_file_path=os.path.join(dir_path, 'tmp/test.json'),
                                          cache_expiration_time=2)
        models = swagger_client.get_models()
        assert_that(list(models.keys()), equal_to(['TestModel']))

        response['definitions']['TestModel2'] = {}

        swagger_client = FdmSwaggerClient(conn=MockConnection(),
                                          cache_file_path=os.path.join(dir_path, 'tmp/test.json'),
                                          cache_expiration_time=2)
        models = swagger_client.get_models()
        assert_that(list(models.keys()), equal_to(['TestModel']))

        time.sleep(2)

        swagger_client = FdmSwaggerClient(conn=MockConnection(),
                                          cache_file_path=os.path.join(dir_path, 'tmp/test.json'),
                                          cache_expiration_time=2)
        models = swagger_client.get_models()
        assert_that(list(models.keys()), equal_to(['TestModel', 'TestModel2']))
