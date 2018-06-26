from bravado.requests_client import RequestsClient
from bravado.swagger_model import Loader


class SwaggerDocsClient(object):
    def __init__(self, swagger_docs):
        self.swagger_docs = swagger_docs

    @classmethod
    def from_url(cls, spec_url, http_client=None):
        http_client = http_client or RequestsClient()
        loader = Loader(http_client)
        swagger_docs = loader.load_spec(spec_url)
        return cls(swagger_docs)

    def get_model_property_desc(self, model_name, property_name):
        return self.swagger_docs['definitions'][model_name]['properties'][property_name]

    def get_path_param_desc(self, path, method, param_name):
        params = self.swagger_docs['paths'][path][method]['parameters']
        return next((param['description'] for param in params if param['name'] == param_name), '')
