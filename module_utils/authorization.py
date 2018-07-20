import json
from functools import wraps

from ansible.module_utils.urls import open_url
from ansible.module_utils.six.moves.urllib.error import HTTPError
from ansible.module_utils.basic import to_text

AUTH_HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}
AUTH_PREFIX = '/api/fdm/v2/fdm/token'
TOKEN_EXPIRATION_STATUS_CODE = 408
UNAUTHORIZED_STATUS_CODE = 401


def request_token(hostname, username, password):
    auth_payload = {
        'grant_type': 'password',
        'username': username,
        'password': password
    }
    url = hostname + AUTH_PREFIX
    response = open_url(url, method='POST', data=json.dumps(auth_payload), headers=AUTH_HEADERS).read()
    return json.loads(to_text(response))


def refresh_token(hostname, refresh_token):
    auth_payload = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }
    url = hostname + AUTH_PREFIX
    response = open_url(url, method='POST', data=json.dumps(auth_payload), headers=AUTH_HEADERS).read()
    return json.loads(to_text(response))


def revoke_token(hostname, access_token, refresh_token):
    logout_payload = {
        'grant_type': 'revoke_token',
        'access_token': access_token,
        'token_to_revoke': refresh_token
    }
    url = hostname + AUTH_PREFIX
    open_url(url, method='POST', data=json.dumps(logout_payload), headers=AUTH_HEADERS)


def retry_on_token_expiration(func):
    @wraps(func)
    def f_retry(*args, **kwargs):

        def refresh_expired_token(params):
            response = refresh_token(params['hostname'], params['refresh_token'])
            params['access_token'], params['refresh_token'] = response['access_token'], response['refresh_token']
            return params

        try:
            return func(*args, **kwargs)
        except HTTPError as e:
            if e.code == TOKEN_EXPIRATION_STATUS_CODE or e.code == UNAUTHORIZED_STATUS_CODE:
                args = (refresh_expired_token(args[0]),) + args[1:]
                return func(*args, **kwargs)
            else:
                raise e

    return f_retry
