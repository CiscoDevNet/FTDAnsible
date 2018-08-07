from enum import Enum

OPERATIONS = 'operations'
SCHEMA = 'schema'
PARAMETERS_FIELD = 'parameters'
MODELS = 'models'
REF = '$ref'
ALL_OF = 'allOf'


class Resource(Enum):
    URL = 'url'
    SPEC = 'spec'


class FdmSwaggerParser:
    _definitions = None

    def pars_spec(self, spec):
        self._definitions = spec['definitions']
        _config = {
            MODELS: self._definitions
        }
        _paths_dict = spec['paths']

        _operations_dict = {}
        for _url, _operation_params in list(_paths_dict.items()):
            for _method, _params in list(_operation_params.items()):
                _operation_id = _params['operationId']
                _operation = {
                    'method': _method,
                    'url': _url,
                    'modelName': self._get_model_name(_method, _params)
                }
                if PARAMETERS_FIELD in _params:
                    _operation[PARAMETERS_FIELD] = self._get_rest_params(_params[PARAMETERS_FIELD])
                _operations_dict[_operation_id] = _operation
        _config[OPERATIONS] = _operations_dict
        return _config

    def _get_model_name(self, _method, _params):
        if _method == 'get':
            return self._get_model_name_from_responses(_params)
        elif _method == 'post' or _method == 'put':
            return self._get_model_name_for_post_put_requests(_params)
        else:
            return None

    def _get_model_name_for_post_put_requests(self, params):
        model_name = None
        if PARAMETERS_FIELD in params:
            _body_param_dict = self._get_body_param_form_parameters(params[PARAMETERS_FIELD])
            if _body_param_dict:
                _schema_ref = _body_param_dict[SCHEMA][REF]
                model_name = self._get_model_name_by_schema_ref(_schema_ref)
        if model_name is None:
            model_name = self._get_model_name_from_responses(params)
        return model_name

    @staticmethod
    def _get_body_param_form_parameters(params):
        for param in params:
            if param['in'] == 'body':
                return param

    def _get_model_name_from_responses(self, params):
        _responses = params['responses']
        if '200' in _responses:
            response = _responses['200'][SCHEMA]
            if REF in response:
                return self._get_model_name_by_schema_ref(response[REF])
            elif 'properties' in response:
                ref = response['properties']['items']['items'][REF]
                return self._get_model_name_by_schema_ref(ref)
            elif ('type' in response) and response['type'] == "file":
                return '_File'
        else:
            return None

    def _get_rest_params(self, params):
        path = {}
        query = {}
        _param = {
            'path': path,
            'query': query
        }
        for param in params:
            in_parm = param['in']
            if in_parm == 'query':
                query[param['name']] = self._simplify_param_def(param)
            elif in_parm == 'path':
                path[param['name']] = self._simplify_param_def(param)
        return _param

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
        _path = _schema_ref.split('/')
        return _path[len(_path) - 1]


class FdmSwaggerClient:
    __config = None

    # TODO:2018-08-06:alexander.vorkov: pass the url or path to file.
    # TODO:2018-08-06:alexander.vorkov: pass the connection object
    def __init__(self, resource=Resource.URL, spec=None):
        if spec:
            self.__config = FdmSwaggerParser().pars_spec(spec)

    def get_operations(self):
        return self.__config[OPERATIONS]

    def get_operation(self, operation_name):
        return self.get_operations().get(operation_name, None)

    def get_models(self):
        return self.__config[MODELS]

    def get_model(self, model_name):
        return self.get_models().get(model_name, None)

    def _from_url(self):
        pass

    def _from_spec(self):
        pass
