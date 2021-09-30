from __future__ import absolute_import, division, print_function

__metaclass__ = type

from copy import deepcopy

from ansible_collections.cisco.ftdansible.plugins.module_utils.configuration import OperationChecker, QueryParams, OperationNamePrefix
from ansible_collections.cisco.ftdansible.plugins.module_utils.fdm_swagger_client import SpecProp, OperationField, OperationParams, PropName, PathParams


class ApiSpecAutocomplete(object):
    """Allow us to extend API spec with custom actions implemented at Module level.

    Should be extended with _check_and_generate_<operation_type>_specs methods - each of which can extend api spec
    with specific operation types.
    The following methods should be called in case of 'api_spec' update required
        _add_operation_to_model_spec
        _add_operation_to_operations_spec
    """
    UPSERT_DEFAULT_FILTER_COMMENT = " Default filtering for Upsert operation is done by name."

    def __init__(self, api_spec):
        self._api_spec = api_spec
        self._operation_checker = OperationChecker

    def _add_operation_to_model_spec(self, model_name, op_name, op_spec):
        self._api_spec[SpecProp.MODEL_OPERATIONS][model_name][op_name] = op_spec

    def _add_operation_to_operations_spec(self, op_name, op_spec):
        self._api_spec[SpecProp.OPERATIONS][op_name] = op_spec

    def _generate_upsert_spec(self, operations, model_name, edit_operation, list_operation):
        op_spec = deepcopy(operations[edit_operation])
        base_filter_spec = deepcopy(
            operations[list_operation][OperationField.PARAMETERS][OperationParams.QUERY].get(QueryParams.FILTER, None))

        def property_for_filtering_is_present(model_spec, prop_name):
            """Check that required property is present in the model spec."""
            return model_spec[PropName.PROPERTIES].get(prop_name)

        if base_filter_spec:
            if property_for_filtering_is_present(model_spec=self._api_spec[SpecProp.MODELS][model_name],
                                                 prop_name=PropName.NAME):
                base_filter_spec[PropName.DESCRIPTION] += self.UPSERT_DEFAULT_FILTER_COMMENT
            else:
                base_filter_spec[PropName.REQUIRED] = True

            op_spec[OperationField.PARAMETERS][OperationParams.QUERY][QueryParams.FILTER] = base_filter_spec
        op_spec[OperationField.PARAMETERS][OperationParams.PATH].pop(PathParams.OBJ_ID, None)

        return op_spec

    def _check_and_generate_upsert_specs(self, model_name, operations):
        """Update api spec if upsert action is applicable to model."""
        # We assume that Upsert and Add actions signature will be same for the moment
        if not model_name:
            # Some actions will have no model - we can't do upsert for them.
            return

        edit_operation = OperationNamePrefix.EDIT + model_name
        list_operation = OperationNamePrefix.GET + model_name + 'List'

        if self._operation_checker.is_upsert_operation_supported(operations):
            op_name = OperationNamePrefix.UPSERT + model_name
            op_spec = self._generate_upsert_spec(operations, model_name, edit_operation, list_operation)

            self._add_operation_to_model_spec(
                model_name=model_name,
                op_name=op_name,
                op_spec=op_spec
            )
            self._add_operation_to_operations_spec(
                op_name=op_name,
                op_spec=op_spec
            )

    def lookup_and_complete(self):
        for model_name, operations in self._api_spec[SpecProp.MODEL_OPERATIONS].items():
            self._check_and_generate_upsert_specs(model_name, operations)
