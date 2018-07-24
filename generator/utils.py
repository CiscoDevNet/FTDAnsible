import json
import re

from ansible.module_utils.basic import to_text
from ansible.module_utils.urls import open_url

AUTH_HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}
AUTH_PREFIX = '/api/fdm/v2/fdm/token'


def request_token(hostname, username, password):
    auth_payload = {
        'grant_type': 'password',
        'username': username,
        'password': password
    }
    response = open_url(hostname + AUTH_PREFIX, method='POST', data=json.dumps(auth_payload), headers=AUTH_HEADERS).read()
    return json.loads(to_text(response))


def revoke_token(hostname, access_token, refresh_token):
    logout_payload = {
        'grant_type': 'revoke_token',
        'access_token': access_token,
        'token_to_revoke': refresh_token
    }
    open_url(hostname + AUTH_PREFIX, method='POST', data=json.dumps(logout_payload), headers=AUTH_HEADERS)


def camel_to_snake(text):
    test_with_underscores = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', test_with_underscores).lower()
