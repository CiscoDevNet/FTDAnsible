from docs.snippets_generation import body_generator


def generate_sample(op_name, op_spec, data_params_are_present, model_name, full_spec, jinja_env):
    template_name = "snippet_bravado.j2"
    operation_arguments = {
        k: '"{}"'.format(v['type'])
        for k, v in op_spec.get("parameters", {}).get('path', {}).items()
    }

    if data_params_are_present:
        body = body_generator.generate_model_sample(
            model_name,
            full_spec
        )
        operation_arguments["body"] = str(body).replace(', ', ", \n\t\t")

    template = jinja_env.get_template(template_name)
    return template.render(
        var=op_spec['tags'][0].lower(),
        tag=op_spec['tags'][0],
        operation=op_name,
        operation_arguments=operation_arguments
    )
