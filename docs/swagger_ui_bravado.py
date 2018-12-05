from . import body_generation


def generate_sample(op_name, op_spec, data_params, full_spec, jinja_env):
    template_name = "snippet_bravado.j2"
    opertaion_arguments = {
        k: '"{}"'.format(v['type'])
        for k,v in op_spec.get("parameters", {}).get('path', {}).items()
    }

    if data_params:
        body = body_generation.body_generator(data_params, full_spec)
        opertaion_arguments["body"] = str(body).replace(', ', ", \n\t\t")

    template = jinja_env.get_template(template_name)
    return template.render(
        var=op_spec['tags'][0].lower(),
        tag=op_spec['tags'][0],
        operation=op_name,
        opertaion_arguments=opertaion_arguments
    )
