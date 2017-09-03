# -*- coding: utf-8 -*-
"""
Any modifications to the falcon framework are consolidated here
"""
import json

import falcon


def falcon_error_serializer(_: falcon.Request,
                            resp: falcon.Response,
                            exc: falcon.HTTPError) -> None:
    """ Serializer for native falcon HTTPError exceptions.

    Serializes HTTPError classes as proper json:api error
        see: http://jsonapi.org/format/#errors
    """
    error = {
        'title': exc.title,
        'detail': exc.description,
        'status': exc.status[0:3],
    }

    if hasattr(exc, "link") and exc.link is not None:
        error['links'] = {'about': exc.link['href']}

    resp.body = json.dumps({'errors': [error]})
