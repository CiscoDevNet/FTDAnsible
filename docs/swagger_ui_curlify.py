"""
Content of the file is just Python implementation of the curlify functionality implemented in SwaggerUI
Original implementation: https://github.com/swagger-api/swagger-ui/blob/master/src/core/curlify.js
"""
import json
from . import body_generation


def curlify(op_spec, data_params, full_spec, base_headers):
    # add mandatory token
    base_headers["Authorization"] = 'Bearer ${ACCESS_TOKEN}'
    http_method = op_spec.get("method").upper()
    curlified = [
        "curl",
        " -X",
        " ",
        http_method,
        " \\"
    ]
    formatter = "\n\t"
    for h, v in base_headers.items():
        curlified.append('{}--header "{}: {}" \\'.format(formatter, h, v))

    if data_params:
        body = body_generation.body_generator(data_params, full_spec)
        curlified.append(
            "{}-d '{}' \\".format(
                formatter,
                json.dumps(
                    body, indent=4
                ).replace("\n", formatter)
            )
        )

    curlified.append('{}"https://${{HOST}}:${{PORT}}{}"'.format(formatter, op_spec.get("url")))

    result = "".join(curlified)

    return result
