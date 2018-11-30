"""
Content of the file is just Python implementation of the curlify functionality implemented in SwaggerUI
Original implementation: https://github.com/swagger-api/swagger-ui/blob/master/src/core/curlify.js
"""
import json


def _generate_spec_for_reference(ref, full_spec):
    model_name = ref.replace("#/definitions/", "")
    model_spec = full_spec[model_name]
    model_spec = model_spec.get("properties", model_spec)
    return _body_generator(model_spec, full_spec)


def _get_default_value(value):
    if value.get("default"):
        return value["default"]
    elif value["type"] == "integer":
        return 0
    elif value["type"] == "boolean":
        return True
    else:
        return value["type"]


def _body_generator(data_params, full_spec):
    result = {}

    if "enum" in data_params:
        return data_params["enum"][0]

    for k, v in data_params.items():
        if v["type"] == "array":
            sample = []
            if v["required"]:
                if "$ref" in v["items"]:
                    sample.append(
                        _generate_spec_for_reference(v["items"]["$ref"], full_spec)
                    )
                else:
                    sample.append(
                        _get_default_value(v["items"])
                    )
        elif v["type"] == "object":
            if "$ref" in v:
                sample = _generate_spec_for_reference(v["$ref"], full_spec)
            else:
                sample = {}
        else:
            sample = _get_default_value(v)

        result[k] = sample

    return result


def curlify(op_spec, data_params, full_spec, base_headers):
    http_method = op_spec.get("method").upper()
    curlified = [
        "curl",
        "-X",
        http_method,
        '"https://${{HOST}}:${{PORT}}{}"'.format(op_spec.get("url"))
    ]

    for h, v in base_headers.items():
        curlified.append('-H "{}: {}"'.format(h, v))

    if data_params:
        body = _body_generator(data_params, full_spec)
        curlified.append(
            "-d '{}'".format(json.dumps(
                body
            ).replace("/\\n/g", ""))
        )

    result = " ".join(curlified)

    return result
