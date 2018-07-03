from collections import namedtuple

SWAGGER_ANSIBLE_TYPE_MAPPING = {
    'string': 'str',
    'boolean': 'bool',
    'array': 'list',
    'object': 'dict',
    'integer': 'int'
}
REFERENCE_MODEL = '#/definitions/ReferenceModel'

ParamSpec = namedtuple("ParamSpec", "name type description required")


class SwaggerParamAdapter(object):
    def __init__(self, swagger_docs):
        self.swagger_docs = swagger_docs

    def get_body_params(self, operation):
        params = {}

        def append_model_params(model_def):
            for property_name, property_spec in model_def._model_spec['properties'].items():
                param_desc = self.swagger_docs.get_model_property_desc(model_name, property_name)
                is_required = property_name in model_def._model_spec['required']
                params[property_name] = ParamSpec(property_name, self.infer_param_type(property_spec), param_desc, is_required)

        for param_name, param in operation.params.items():
            if param.param_spec['in'] != 'body':
                continue

            model_ref = param.param_spec['schema']['$ref']
            model_name = model_ref[len('#/definitions/'):]
            append_model_params(operation.swagger_spec.definitions[model_name])

        return params

    def get_path_params(self, operation):
        return self._find_url_params(operation, 'path')

    def get_query_params(self, operation):
        return self._find_url_params(operation, 'query')

    def _find_url_params(self, operation, url_part):
        params = {}
        for param_name, param in operation.params.items():
            if param.param_spec['in'] != url_part:
                continue
            param_desc = self.swagger_docs.get_path_param_desc(operation.path_name, operation.http_method, param_name)
            params[param_name] = ParamSpec(param_name, self.infer_param_type(param.param_spec), param_desc, param.required)
        return params

    @staticmethod
    def infer_param_type(param_spec):
        def is_enum():
            return param_spec['type'] == 'object' and param_spec['$ref'] != REFERENCE_MODEL

        if 'type' in param_spec:
            return 'str' if is_enum() else SWAGGER_ANSIBLE_TYPE_MAPPING[param_spec['type']]
        else:
            return 'dict'

    @staticmethod
    def get_unique_params(operations):
        params = []
        for operation in operations.values():
            params = params + list(operation['path_params'].values()) + list(operation['body_params'].values()) + list(
                operation['query_params'].values())
        return sorted(set(params))
