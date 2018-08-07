from enum import Enum


class Resource(Enum):
    URL = 'url'
    SPEC = 'spec'


class FdmSwaggerParser:
    _definitions = None

    def pars_spec(self, spec):
        self._definitions = spec['definitions']
        _config = {
            'models': self._definitions
        }
        _paths_dict = spec['paths']

        _operations_dict = {}
        for _url, _operation_params in list(_paths_dict.items()):
            for _method, _params in list(_operation_params.items()):
                _operation_id = _params['operationId']
                _operations_dict[_operation_id] = {
                    'method': _method,
                    'url': _url,
                    'modelName': self._get_model_name(_method, _params),
                    'parameters': self._get_rest_params(_params['parameters'])
                }
        _config['operations'] = _operations_dict
        return _config

    def _get_model_name(self, _method, _params):
        if _method == 'get':
            return self._get_model_name_for_get_request(_params)
        elif _method == 'post' or _method == 'put':
            return self._get_model_name_for_post_put_requests(_params)
        else:
            return None

    def _get_model_name_for_post_put_requests(self, _params):
        _body_param_dict = self._get_body_param_form_parameters(_params['parameters'])
        _schema_ref = _body_param_dict['schema']['$ref']
        return self._get_model_name_by_schema_ref(_schema_ref)

    @staticmethod
    def _get_body_param_form_parameters(params):
        for param in params:
            if param['in'] == 'body':
                return param

    def _get_model_name_for_get_request(self, params):
        response = params['responses']['200']['schema']
        if '$ref' in response:
            return self._get_model_name_by_schema_ref(response['$ref'])
        elif 'properties' in response:
            ref = response['properties']['items']['items']['$ref']
            return self._get_model_name_by_schema_ref(ref)

    def _get_rest_params(self, params):
        path = {}
        query = {}
        _param = {
            'path': path,
            'query': query
        }
        for param in params:
            if param['in'] == 'query':
                query[param['name']] = self._simplify_param_def(param)
            elif param['in'] == 'path':
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
        if 'allOf' in model_def:
            return self._get_model_name_by_schema_ref(model_def['allOf'][0]['$ref'])
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
        return self.__config['operations']

    def get_operation(self, operation_name):
        return self.get_operations().get(operation_name, None)

    def get_models(self):
        return self.__config['models']

    def get_model(self, model_name):
        return self.get_models().get(model_name, None)

    def _from_url(self):
        pass

    def _from_spec(self):
        pass
