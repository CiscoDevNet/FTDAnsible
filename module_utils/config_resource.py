from functools import partial

from ansible.module_utils._text import to_text
from ansible.module_utils.http import iterate_over_pageable_resource
from ansible.module_utils.misc import equal_objects
from ansible.module_utils.six.moves.urllib.error import HTTPError


class BaseConfigObjectResource(object):
    def __init__(self, conn):
        self._conn = conn
        self.config_changed = False

    def get_object_by_name(self, url_path, name, path_params=None):
        get_object_list = partial(self._conn.send_request, url_path=url_path, http_method='GET',
                                  path_params=path_params)

        item_generator = iterate_over_pageable_resource(
            lambda query_params: get_object_list(query_params=query_params),
            {'filter': 'name:%s' % name}
        )
        # not all endpoints support filtering so checking name explicitly
        return next((item for item in item_generator if item['name'] == name), None)

    def add_object(self, url_path, body_params, path_params=None, query_params=None):
        existing_obj = self.get_object_by_name(url_path, body_params['name'], path_params)

        if not existing_obj:
            return self._send_modifying_request(url_path=url_path, http_method='POST', body_params=body_params,
                                                path_params=path_params, query_params=query_params)
        elif equal_objects(existing_obj, body_params):
            return existing_obj
        else:
            raise ValueError(
                'Cannot add new object. An object with the same name but different parameters already exists.')

    def delete_object(self, url_path, path_params):
        def is_invalid_uuid_error(err):
            err_msg = to_text(err.read())
            return err.code == 422 and "Validation failed due to an invalid UUID" in err_msg

        try:
            return self._send_modifying_request(url_path=url_path, http_method='DELETE', path_params=path_params)
        except HTTPError as e:
            if is_invalid_uuid_error(e):
                return {'response': 'Referenced object does not exist'}
            else:
                raise e

    def edit_object(self, url_path, body_params, path_params=None, query_params=None):
        existing_object = self._conn.send_request(url_path=url_path, http_method='GET', path_params=path_params)

        if not existing_object:
            raise ValueError('Referenced object does not exist')
        elif equal_objects(existing_object, body_params):
            return existing_object
        else:
            return self._send_modifying_request(url_path=url_path, http_method='PUT', body_params=body_params,
                                                path_params=path_params, query_params=query_params)

    def _send_modifying_request(self, url_path, http_method, body_params=None, path_params=None, query_params=None):
        response = self._conn.send_request(url_path=url_path, http_method=http_method, body_params=body_params,
                                           path_params=path_params, query_params=query_params)
        self.config_changed = True
        return response
