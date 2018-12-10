"""
Content of the file is just Python implementation of the curlify functionality implemented in SwaggerUI
Original implementation: https://github.com/swagger-api/swagger-ui/blob/master/src/core/curlify.js
"""
from docs.snippets_generation import body_generator


def generate_sample(op_spec, data_params_are_present, model_name, full_spec, base_headers, jinja_env):
    body = None
    template_name = "snippet_curl.j2"
    headers = dict(base_headers)
    # add mandatory token
    headers["Authorization"] = 'Bearer ${ACCESS_TOKEN}'
    headers.pop('User-Agent', None)
    if data_params_are_present:
        body = body_generator.generate_model_sample(model_name, full_spec)

    template = jinja_env.get_template(template_name)
    return template.render(
        http_method=op_spec.get("method"),
        headers=headers,
        body=body,
        url=op_spec.get("url")
    )
