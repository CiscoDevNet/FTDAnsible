DEFAULT_PAGE_SIZE = 10
DEFAULT_TIMEOUT = 60 * 10  # 10 minutes


class HTTPMethod:
    GET = 'get'
    POST = 'post'
    PUT = 'put'
    DELETE = 'delete'


def iterate_over_pageable_resource(resource, params):
    params['limit'] = DEFAULT_PAGE_SIZE
    params['offset'] = 0

    result = resource(params)
    while result['items']:
        for item in result['items']:
            yield item
        params['offset'] += DEFAULT_PAGE_SIZE
        result = resource(params)
