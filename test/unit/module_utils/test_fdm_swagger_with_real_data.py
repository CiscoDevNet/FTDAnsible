import json
import os
import unittest

try:
    from ansible.module_utils.fdm_swagger_client import FdmSwaggerValidator, FdmSwaggerParser
except ImportError:
    from module_utils.fdm_swagger_client import FdmSwaggerValidator, FdmSwaggerParser
DIR_PATH = os.path.dirname(os.path.realpath(__file__))
TEST_DATA_FOLDER = os.path.join(DIR_PATH, 'test_data')


class TestFdmSwagger(unittest.TestCase):

    def setUp(self):
        self.init_mock_data()

    def init_mock_data(self):
        with open(os.path.join(TEST_DATA_FOLDER, 'ngfw_with_ex.json')) as f:
            self.base_data = json.load(f)

    def test_with_all_data(self):
        fdm_data = FdmSwaggerParser().parse_spec(self.base_data)
        validator = FdmSwaggerValidator(fdm_data)
        models = fdm_data['models']
        operations = fdm_data['operations']

        invalid = []
        for operation in operations:
            model_name = operations[operation]['modelName']
            method = operations[operation]['method']
            if method != 'get' and model_name in models:
                if 'example' in models[model_name]:
                    example = models[model_name]['example']
                    try:
                        valid, rez = validator.validate_data(operation, example)
                        assert valid
                    except Exception as e:
                        invalid.append(model_name)
        assert sorted(invalid) == sorted(['TCPPortObject', 'TCPPortObject',
                                          'UDPPortObject', 'UDPPortObject', 'ICMPv4PortObject',
                                          'ICMPv4PortObject', 'ICMPv6PortObject', 'ICMPv6PortObject',
                                          'StandardAccessList', 'StandardAccessList',
                                          'ExtendedAccessList', 'ExtendedAccessList',
                                          'ASPathList', 'ASPathList',
                                          'RouteMap', 'RouteMap',
                                          'StandardCommunityList', 'StandardCommunityList',
                                          'ExpandedCommunityList', 'ExpandedCommunityList',
                                          'IPV4PrefixList', 'IPV4PrefixList',
                                          'IPV6PrefixList', 'IPV6PrefixList',
                                          'PolicyList', 'PolicyList',
                                          'SyslogServer', 'SyslogServer',
                                          'HAConfiguration',
                                          'TestIdentitySource'])

    def test_parse_all_data(self):
        self.fdm_data = FdmSwaggerParser().parse_spec(self.base_data)
        operations = self.fdm_data['operations']
        without_model_name = []
        expected_operations_counter = 0
        for key in self.base_data['paths']:
            operation = self.base_data['paths'][key]
            for _ in operation:
                expected_operations_counter += 1

        for key in operations:
            operation = operations[key]
            if not operation['modelName'] and (operation['method'] != 'delete'):
                without_model_name.append(operation['url'])

            if operation['modelName'] == '_File' and 'download' not in operation['url']:
                self.fail('File type can be defined for download operation only')

        assert ['/api/fdm/v2/action/upgrade'] == without_model_name
        assert expected_operations_counter == len(operations)
