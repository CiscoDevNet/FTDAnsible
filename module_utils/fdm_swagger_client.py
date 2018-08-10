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
        model_name = self._get_model_name_from_url(_schema_ref)
        model_def = self._definitions[model_name]
        if ALL_OF in model_def:
            return self._get_model_name_by_schema_ref(model_def[ALL_OF][0][REF])
        else:
            return model_name

    @staticmethod
    def _get_model_name_from_url(_schema_ref):
        path = _schema_ref.split('/')
        return path[len(path) - 1]
