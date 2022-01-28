from __future__ import absolute_import, division, print_function

__metaclass__ = type

from pprint import PrettyPrinter

from ansible_collections.cisco.ftdansible.plugins.module_utils.fdm_swagger_client import OperationField

from docs.snippets_generation import body_generator
from docs import utils


def generate_sample(op_name, op_spec, data_params_are_present, model_name, full_spec, jinja_env):
    template_name = "snippet_bravado.j2"
    operation_arguments = {
        k: '"%s"' % (v['type'])
        for k, v in op_spec.get("parameters", {}).get('path', {}).items()
    }

    if data_params_are_present:
        body = body_generator.generate_model_sample(
            model_name,
            full_spec
        )
        body = utils.filter_data_params(op_name, op_spec[OperationField.METHOD], body)
        printer = PrettyPrinter(width=1)
        operation_arguments["body"] = printer.pformat(body)

    template = jinja_env.get_template(template_name)
    return template.render(
        var=op_spec['tags'][0].lower(),
        tag=op_spec['tags'][0],
        operation=op_name,
        operation_arguments=operation_arguments
    )
