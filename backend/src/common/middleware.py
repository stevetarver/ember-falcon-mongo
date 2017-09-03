# -*- coding: utf-8 -*-
"""
Falcon middleware

REFERENCES:
    https://falcon.readthedocs.io/en/stable/api/middleware.html
"""
import json
from datetime import datetime
from uuid import uuid4

import falcon

from .logging import LogEntryProcessor, LoggerMixin


class Telemetry(LoggerMixin):
    """
    CAVEATS:
        We really want to log the body on ingress but it is provided as a non-seekable
        stream from the WSGI server - so once read, it is gone. We read the body and
        store it in req.context['body_json'] - all api layer handlers that expect a
        body must find it there.
    """
    def __init__(self):
        super(Telemetry, self).__init__()
        self._excluded_resources = ('/liveness', '/readiness', '/ping')

    def process_request(self, req: falcon.Request, _: falcon.Response) -> None:
        """
        Process the request before routing it.
        """
        if req.path not in self._excluded_resources:
            req.context['received_at'] = datetime.now()
            req.context['body_json'] = {}
            if req.content_length:
                req.context['body_json'] = json.load(req.bounded_stream)
            self._info("Request received",
                       logCategory='apiRequest',
                       reqReferrer=', '.join(req.access_route),
                       reqVerb=req.method,
                       reqPath=req.path,
                       reqQuery=req.query_string,
                       reqBody=req.context['body_json'])

    def process_response(self, req: falcon.Request, resp: falcon.Response, _, __: bool) -> None:
        """
        Post-processing of the response (after routing)
        :param req:
        :param resp:
        :param resource: Resource object to which the request was routed. May
            be None if no route was found for the request.
        :param req_succeeded: True if no exceptions were raised while the
            framework processed and routed the request; otherwise False.
        :return:
        """
        if req.path not in self._excluded_resources:
            status = 0
            try:
                status = int(resp.status[0:3])
            except:  # pylint: disable=bare-except
                pass # intentionally ignore

            duration = int((datetime.now() - req.context['received_at']).total_seconds() * 1000000)
            self._info("Request completed",
                       logCategory='apiResponse',
                       reqDurationMicros=duration,
                       reqStatusCode=status)


class RequestId:

    def process_request(self, req: falcon.Request, _: falcon.Response) -> None:
        """
        Provide a request id for tying together all log entries made during
        request processing. If the client provided a x-request-id, use that,
        otherwise generate one.
        """
        LogEntryProcessor.set_request_id(req.get_header('x-request-id', default=str(uuid4())))

    def process_response(self, _: falcon.Request, __: falcon.Response, ___, ____: bool) -> None:
        """
        Remove x-request-id from thread local storage in preparation for next request
        """
        LogEntryProcessor.set_request_id(None)
