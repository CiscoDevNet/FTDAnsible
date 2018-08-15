from ansible.module_utils.six import integer_types, string_types

try:
    from ansible.module_utils.http import HTTPMethod
except (ImportError, ModuleNotFoundError):
    from module_utils.http import HTTPMethod

MODEL_NAME_FIELD = 'modelName'
URL_FIELD = 'url'
METHOD_FIELD = 'method'
PARAMETERS_FIELD = 'parameters'

PATHS = 'paths'
OPERATION_ID = 'operationId'
FILE_MODEL_NAME = '_File'
SUCCESS_RESPONSE_CODE = '200'
BASE_PATH = 'basePath'
DEFINITIONS = 'definitions'
OPERATIONS = 'operations'
SCHEMA = 'schema'
MODELS = 'models'
REF = '$ref'
ALL_OF = 'allOf'


def _get_model_name_from_url(_schema_ref):
    path = _schema_ref.split('/')
    return path[len(path) - 1]


class FdmSwaggerParser:
    _definitions = None

    def parse_spec(self, spec):
        self._definitions = spec[DEFINITIONS]
        config = {
            MODELS: self._definitions,
            OPERATIONS: self._get_operations(spec)
        }
        return config

    def _get_operations(self, spec):
        base_path = spec[BASE_PATH]
        paths_dict = spec[PATHS]
        operations_dict = {}
        for url, operation_params in paths_dict.items():
            for method, params in operation_params.items():
                operation = {
                    METHOD_FIELD: method,
                    URL_FIELD: base_path + url,
                    MODEL_NAME_FIELD: self._get_model_name(method, params)
                }
                if PARAMETERS_FIELD in params:
                    operation[PARAMETERS_FIELD] = self._get_rest_params(params[PARAMETERS_FIELD])

                operation_id = params[OPERATION_ID]
                operations_dict[operation_id] = operation
        return operations_dict

    def _get_model_name(self, method, params):
        if method == HTTPMethod.GET:
            return self._get_model_name_from_responses(params)
        elif method == HTTPMethod.POST or method == HTTPMethod.PUT:
            return self._get_model_name_for_post_put_requests(params)
        else:
            return None

    def _get_model_name_for_post_put_requests(self, params):
        model_name = None
        if PARAMETERS_FIELD in params:
            body_param_dict = self._get_body_param_from_parameters(params[PARAMETERS_FIELD])
            if body_param_dict:
                schema_ref = body_param_dict[SCHEMA][REF]
                model_name = self._get_model_name_by_schema_ref(schema_ref)
        if model_name is None:
            model_name = self._get_model_name_from_responses(params)
        return model_name

    @staticmethod
    def _get_body_param_from_parameters(params):
        return next((param for param in params if param['in'] == 'body'), None)

    def _get_model_name_from_responses(self, params):
        responses = params['responses']
        if SUCCESS_RESPONSE_CODE in responses:
            response = responses[SUCCESS_RESPONSE_CODE][SCHEMA]
            if REF in response:
                return self._get_model_name_by_schema_ref(response[REF])
            elif 'properties' in response:
                ref = response['properties']['items']['items'][REF]
                return self._get_model_name_by_schema_ref(ref)
            elif ('type' in response) and response['type'] == "file":
                return FILE_MODEL_NAME
        else:
            return None

    def _get_rest_params(self, params):
        path = {}
        query = {}
        operation_param = {
            'path': path,
            'query': query
        }
        for param in params:
            in_param = param['in']
            if in_param == 'query':
                query[param['name']] = self._simplify_param_def(param)
            elif in_param == 'path':
                path[param['name']] = self._simplify_param_def(param)
        return operation_param

    @staticmethod
    def _simplify_param_def(param):
        return {
            'type': param['type'],
            'required': param['required']
        }

    def _get_model_name_by_schema_ref(self, _schema_ref):
        model_name = _get_model_name_from_url(_schema_ref)
        model_def = self._definitions[model_name]
        if ALL_OF in model_def:
            return self._get_model_name_by_schema_ref(model_def[ALL_OF][0][REF])
        else:
            return model_name


class PropType:
    STRING = 'string'
    BOOLEAN = 'boolean'
    INTEGER = 'integer'
    NUMBER = 'number'
    OBJECT = 'object'
    ARRAY = 'array'


class PronName:
    ENUM = 'enum'
    TYPE = 'type'


class FdmSwaggerValidator:
    def __init__(self, spec):
        self._operations = spec['operations']
        self._models = spec['models']

    def validate_query_params(self, operation, params):
        pass

    def validate_path_params(self, operation, params):
        pass

    def validate_data(self, operation, data, skip_fields=None):
        if skip_fields is None:
            skip_fields = []

        operation = self._operations[operation]
        model = self._models[operation['modelName']]
        status = {
            'required': [],
            'invalid_type': []
        }
        self._validate_object(status, model, data, '', skip_fields)

        if len(status['required']) > 0 or len(status['invalid_type']) > 0:
            status['status'] = 'invalid'
            return status
        return {'status': 'valid'}

    def _validate_object(self, status, model, data, path, skip_fields=None):
        if skip_fields is None:
            skip_fields = []

        if self._is_enum(model):
            self._check_enum(status, model, data, path)
        elif self._is_object(model):
            self._check_object(status, model, data, path, skip_fields)

    @staticmethod
    def _is_enum(model):
        return FdmSwaggerValidator._is_string_type(model) and PronName.ENUM in model

    @staticmethod
    def _is_string_type(model):
        return PronName.TYPE in model and model[PronName.TYPE] == PropType.STRING

    def _check_enum(self, status, model, value, path):
        if value not in model[PronName.ENUM]:
            self._add_invalid_type_report(status, path, '', PronName.ENUM, value)

    @staticmethod
    def _add_invalid_type_report(status, path, prop, expected_type, actually_value):
        status['invalid_type'].append({
            'path': FdmSwaggerValidator._create_path_to_field(path, prop),
            'expected_type': expected_type,
            'actually_value': actually_value
        })

    @staticmethod
    def _create_path_to_field(path='', field=''):
        separator = ''
        if path and field:
            separator = '.'
        return "{}{}{}".format(path, separator, field)

    @staticmethod
    def _is_object(model):
        return PronName.TYPE in model and model[PronName.TYPE] == PropType.OBJECT

    def _check_object(self, status, model, data, path, skip_fields):
        FdmSwaggerValidator._check_required_fields(status, model['required'], data, path, skip_fields)

        model_properties = model['properties']
        for prop in model_properties.keys():
            if prop in data:
                model_prop_val = model_properties[prop]
                expected_type = model_prop_val[PronName.TYPE]
                actually_value = data[prop]
                self._check_types(status, actually_value, expected_type, model_prop_val, path, prop)

    def _check_types(self, status, actually_value, expected_type, model, path, prop_name):
        if expected_type == PropType.OBJECT:
            ref_model = self._get_model_by_ref(model)

            self._validate_object(status, ref_model, actually_value,
                                  path=self._create_path_to_field(path, prop_name), skip_fields=[])
        elif expected_type == PropType.ARRAY:
            self._check_array(status, model, actually_value,
                              path=self._create_path_to_field(path, prop_name))
        elif not self._is_simple_types(expected_type, actually_value):
            status['invalid_type'].append({
                'path': self._create_path_to_field(path, prop_name),
                'expected_type': expected_type,
                'actually_value': actually_value
            })

    @staticmethod
    def _is_simple_types(model_prop, value):
        # TODO:2018-08-14:alexander.vorkov: Should we support a string version "True", "1" ...?
        if model_prop == PropType.STRING:
            return isinstance(value, string_types)
        elif model_prop == PropType.BOOLEAN:
            return isinstance(value, bool)
        elif model_prop == PropType.INTEGER:
            return isinstance(value, integer_types) and not isinstance(value, bool)
        elif model_prop == PropType.NUMBER:
            return isinstance(value, (integer_types, float)) and not isinstance(value, bool)
        return False

    def _get_model_by_ref(self, model_prop_val):
        model = _get_model_name_from_url(model_prop_val['$ref'])
        return self._models[model]

    @staticmethod
    def _check_required_fields(status, required_fields, data, path, skip_fields):
        missed_required_fields = [FdmSwaggerValidator._create_path_to_field(path, field) for field in
                                  required_fields if
                                  not (field in skip_fields or field in data.keys())]
        if len(missed_required_fields) > 0:
            status['required'] += missed_required_fields

    # TODO:2018-08-14:alexander.vorkov: need to add tests
    def _check_array(self, status, model, actually_value, path):
        item_model = model['items']
        for i, item_data in enumerate(actually_value):
            self._check_types(status, item_data, item_model['type'], item_model, "{}[{}]".format(path, i), '')
