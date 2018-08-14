from ansible.module_utils.six import string_types, integer_types

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
        rez = self._validate_object(status, model, data, '', skip_fields)

        if len(rez['required']) > 0 or len(rez['invalid_type']) > 0:
            status['status'] = 'invalid'
            return status
        return {'status': 'valid'}

    def _validate_object(self, status, model, data, path, skip_fields):
        all_required_fields_passed, missed_required_fields = self._check_required_fields(model['required'], data, path,
                                                                                         skip_fields)
        if not all_required_fields_passed:
            status['required'] += missed_required_fields

        model_properties = model['properties']
        invalid_type = []
        for prop in model_properties.keys():
            if prop in data:
                model_prop_val = model_properties[prop]
                expected_type = model_prop_val[PronName.TYPE]
                actually_value = data[prop]
                if expected_type == PropType.OBJECT:
                    ref_model = self._get_model_by_ref(model_prop_val)
                    if self._is_enum(ref_model):
                        if actually_value not in ref_model[PronName.ENUM]:
                            invalid_type.append({
                                'path': self._create_path_to_field(path, prop),
                                'expected_type': PronName.ENUM,
                                'actually_value': actually_value
                            })
                    else:
                        self._validate_object(status, ref_model, actually_value,
                                              path="{}{}.".format(path, prop), skip_fields=[])
                elif not self._check_types(expected_type, actually_value):
                    invalid_type.append({
                        'path': self._create_path_to_field(path, prop),
                        'expected_type': expected_type,
                        'actually_value': actually_value
                    })
        status['invalid_type'] += invalid_type

        return status

    def _get_model_by_ref(self, model_prop_val):
        model = _get_model_name_from_url(model_prop_val['$ref'])
        return self._models[model]

    def _check_required_fields(self, required_fields, data, path, skip_fields):
        v = [self._create_path_to_field(path, field) for field in required_fields if
             not (field in skip_fields or field in data.keys())]
        if len(v) > 0:
            return False, v
        return True, ""

    @staticmethod
    def _create_path_to_field(path, field):
        return "{}{}".format(path, field)

    @staticmethod
    def _check_types(model_prop, value):
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

    @staticmethod
    def _is_enum(model):
        return model[PronName.TYPE] == PropType.STRING and PronName.ENUM in model
