import json
from functools import partial

from ansible.module_utils.connection import ConnectionError

# TODO: remove import workarounds when module_utils are moved to the Ansible core
try:
    from ansible.module_utils.http import iterate_over_pageable_resource, HTTPMethod
    from ansible.module_utils.misc import equal_objects, copy_identity_properties, ConfigurationError
except (ImportError, ModuleNotFoundError):
    from module_utils.http import iterate_over_pageable_resource, HTTPMethod
    from module_utils.misc import equal_objects, copy_identity_properties, ConfigurationError

UNPROCESSABLE_ENTITY_STATUS = 422
INVALID_UUID_ERROR_MESSAGE = "Validation failed due to an invalid UUID"


class BaseConfigObjectResource(object):
    def __init__(self, conn):
        self._conn = conn
        self.config_changed = False

    def get_object_by_name(self, url_path, name, path_params=None):
        get_object_list = partial(self.send_request, url_path=url_path, http_method=HTTPMethod.GET,
                                  path_params=path_params)

        item_generator = iterate_over_pageable_resource(
            lambda query_params: get_object_list(query_params=query_params),
            {'filter': 'name:%s' % name}
        )
        # not all endpoints support filtering so checking name explicitly
        return next((item for item in item_generator if item['name'] == name), None)

    def add_object(self, url_path, body_params, path_params=None, query_params=None, update_if_exists=False):
        existing_obj = self.get_object_by_name(url_path, body_params['name'], path_params)

        if not existing_obj:
            return self.send_request(url_path=url_path, http_method=HTTPMethod.POST, body_params=body_params,
                                     path_params=path_params, query_params=query_params)
        elif equal_objects(existing_obj, body_params):
            return existing_obj
        elif update_if_exists:
            if path_params is None:
                path_params = {}
            path_params['objId'] = existing_obj['id']
            return self.send_request(url_path=url_path + '/{objId}',
                                     http_method=HTTPMethod.PUT,
                                     body_params=copy_identity_properties(existing_obj, body_params),
                                     path_params=path_params,
                                     query_params=query_params)
        else:
            raise ConfigurationError(
                'Cannot add new object. An object with the same name but different parameters already exists.')

    def delete_object(self, url_path, path_params):
        def is_invalid_uuid_error(err):
            # Ansible does not pass HTTP errors from plugin to module.
            # The only available information is HTTP status stored in the message.
            return err.code == UNPROCESSABLE_ENTITY_STATUS and INVALID_UUID_ERROR_MESSAGE in str(err)

        try:
            return self.send_request(url_path=url_path, http_method=HTTPMethod.DELETE, path_params=path_params)
        except ConnectionError as e:
            if is_invalid_uuid_error(e):
                return {'status': 'Referenced object does not exist'}
            else:
                raise e

    def edit_object(self, url_path, body_params, path_params=None, query_params=None):
        existing_object = self.send_request(url_path=url_path, http_method=HTTPMethod.GET, path_params=path_params)

        if not existing_object:
            raise ConfigurationError('Referenced object does not exist')
        elif equal_objects(existing_object, body_params):
            return existing_object
        else:
            return self.send_request(url_path=url_path, http_method=HTTPMethod.PUT, body_params=body_params,
                                     path_params=path_params, query_params=query_params)

    def send_request(self, url_path, http_method, body_params=None, path_params=None, query_params=None):
        def raise_for_failure(resp):
            if not resp['success']:
                raise ConnectionError(json.dumps(resp['response']), code=resp['status_code'])

        response = self._conn.send_request(url_path=url_path, http_method=http_method, body_params=body_params,
                                           path_params=path_params, query_params=query_params)
        raise_for_failure(response)
        if http_method != HTTPMethod.GET:
            self.config_changed = True
        return response['response']
