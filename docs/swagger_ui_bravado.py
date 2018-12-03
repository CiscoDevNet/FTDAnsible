from . import body_generation


def generate_sample(op_name, op_spec, data_params, full_spec):
    BASE_SAMPLE = """ 
from bravado.requests_client import RequestsClient
from bravado.client import SwaggerClient

HOST = 'ftd.example.com'
AUTH_TOKEN = 'access_token'

http_client = RequestsClient()
http_client.ssl_verify = False
http_client.set_api_key(
     HOST, 
    'Bearer {{}}'.format(AUTH_TOKEN),
    param_name='Authorization', 
    param_in='header'
)
client = SwaggerClient.from_url(
    'https://{{}}/apispec/ngfw.json'.format(HOST),
    http_client=http_client,
    config={{'validate_responses': False, 'validate_swagger_spec': False}}
)

{var} = client.{tag}.{operation}({opertaion_arguments}).response().result
"""

    opertaion_arguments = [
        '{}="{}"'.format(k, v['type'])
        for k,v in op_spec.get("parameters", {}).get('path', {}).items()
    ]

    if data_params:
        body = body_generation.body_generator(data_params, full_spec)
        opertaion_arguments.append(
            'body={}'.format(
                str(body).replace(', ', ", \n\t\t")
            )
        )

    return BASE_SAMPLE.format(
        var=op_spec['tags'][0].lower(),
        tag=op_spec['tags'][0],
        operation=op_name,
        opertaion_arguments=", \n\t".join(opertaion_arguments)
    )