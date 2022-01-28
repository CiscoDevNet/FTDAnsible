# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re

from ansible_collections.cisco.ftdansible.plugins.module_utils.fdm_swagger_client import SpecProp, PropName, PropType


def camel_to_snake(text):
    """
    Lookup and replace words in camelCaseFormat with same words in snake_format.

    :param text: string value.
    :return: updated text value
    """
    test_with_underscores = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', test_with_underscores).lower()


def get_link_to_model_page_by_name(model_name, display_name="object"):
    """
    Generates Markdown hyperlink statement for particular model.

    :param model_name: string value
    :param display_name: string value to be displayed as hyperlink text. default value is "object"
    :return: string value which represents Markdown hyperlink statement
    """
    return "[%s]%s" % (display_name, _get_link_path(model_name))


def _get_link_path(model_name):
    return "(/models/%s.md)" % (camel_to_snake(model_name))


def show_type_or_reference(data_param_spec, api_spec=None):
    """
    Check if particular data parameter represents complex data type but not Enum and generate
    Markdown hyperlink statement which leads user to page with complex data type description.

    :param data_param_spec: dict object with swagger specification of data param
    :param api_spec: dict object which represents complete API spec
    :return: string value which represents simple type or hyperlink to complex type
    """
    data_param_type = data_param_spec.get(PropName.TYPE, PropType.OBJECT)

    def ref_to_model_name(ref_address):
        return ref_address.replace("#/definitions/", "")

    def default_value():
        return data_param_type

    def process_array():
        ref_name = data_param_spec[PropName.ITEMS].get(PropName.REF)
        if ref_name:
            model = ref_to_model_name(ref_name)
            return "[%s]" % (get_link_to_model_page_by_name(model))

        return "[%s]" % (data_param_spec[PropName.ITEMS][PropName.TYPE])

    def process_object():
        if PropName.REF not in data_param_spec:
            return default_value()

        model = ref_to_model_name(data_param_spec[PropName.REF])
        model_api_spec = api_spec[SpecProp.MODELS].get(model, {})

        if PropName.ENUM in model_api_spec:
            return model_api_spec.get(PropName.TYPE, data_param_type)

        return get_link_to_model_page_by_name(model)

    decision_map = {
        PropType.ARRAY: process_array,
        PropType.OBJECT: process_object
    }

    return decision_map.get(data_param_type, default_value)()


def show_description_with_references(description):
    """
    Check if any complex data type mentioned in the description, if so - name of the complex data type replaced with
    hyperlink to page with corresponding data type definition.

    :param description: string value to be checked
    :return: updated description values
    """
    matched_model_names = re.findall("types are: &#91;(.*)&#93;", description)
    if not matched_model_names:
        return description

    model_names = matched_model_names[0].split(', ')

    linked_model_names = [
        get_link_to_model_page_by_name(model, display_name=model)
        for model in model_names
    ]

    return description.replace(
        matched_model_names[0],
        ", ".join(linked_model_names)
    )
