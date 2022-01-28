from __future__ import absolute_import, division, print_function

__metaclass__ = type


def _get_default_value(value, *args):
    if value.get("default"):
        return value["default"]
    elif value["type"] == "integer":
        return 0
    elif value["type"] == "boolean":
        return True
    else:
        return value["type"]


def _get_model_name_from_reference(ref):
    return ref.replace("#/definitions/", "")


def _get_sample_for_array(array_spec, full_spec):
    sample = []
    if array_spec["required"]:
        if "$ref" in array_spec["items"]:
            sample.append(
                generate_model_sample(
                    _get_model_name_from_reference(array_spec["items"]["$ref"]),
                    full_spec
                )
            )
        else:
            sample.append(
                _get_default_value(array_spec["items"])
            )
    return sample


def _get_sample_for_object(obj_spec, full_spec):
    if "$ref" in obj_spec:
        sample = generate_model_sample(
            _get_model_name_from_reference(obj_spec["$ref"]),
            full_spec
        )
    else:
        sample = {}

    return sample


def _generated_sample_by_model_spec(data_params, full_spec):
    result = {}

    if "enum" in data_params:
        return data_params["enum"][0]

    processing_map = {
        "array": _get_sample_for_array,
        "object": _get_sample_for_object
    }

    for key, value in data_params.items():
        value_type = value.get("type", "object")
        result[key] = processing_map.get(value_type, _get_default_value)(value, full_spec)

    return result


def generate_model_sample(model_name, full_spec):
    model_spec = full_spec.get(model_name, {})
    model_spec = model_spec.get("properties", model_spec)
    return _generated_sample_by_model_spec(model_spec, full_spec)
