import time

from ansible.module_utils.six.moves.urllib.parse import urlencode

API_PREFIX = "/api/fdm/v1"

DEFAULT_PAGE_SIZE = 10
DEFAULT_TIMEOUT = 60 * 10  # 10 minutes


def base_headers(token):
    return {
        'Authorization': 'Bearer %s' % token,
        'Content-Type': 'application/json'
    }


def construct_url(hostname, path, path_params=None, query_params=None):
    url = hostname + API_PREFIX + path
    if path_params:
        url = url.format(**path_params)
    if query_params:
        url += "?" + urlencode(query_params)
    return url


def iterate_over_pageable_resource(resource, params):
    params['limit'] = DEFAULT_PAGE_SIZE
    params['offset'] = 0

    result = resource(params)
    while result['items']:
        for item in result['items']:
            yield item
        params['offset'] += DEFAULT_PAGE_SIZE
        result = resource(params)


def wait_for_job_completion(fetch_job_status_func, timeout=DEFAULT_TIMEOUT):
    start = time.time()
    while True:
        time.sleep(1)
        if time.time() > start + timeout:
            raise TimeoutError()

        status = fetch_job_status_func()
        if status['endTime'] != -1:
            return status
