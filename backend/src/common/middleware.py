import falcon
from datetime import datetime
from .logging import LoggerMixin


class Telemetry(LoggerMixin):
    """
    see https://falcon.readthedocs.io/en/stable/api/middleware.html
    """
    def __init__(self):
        super(Telemetry, self).__init__()
        self._excluded_resources = ('/liveness', '/readiness', '/ping')

    def process_request(self, req: falcon.Request, _: falcon.Response) -> None:
        """
        Process the request before routing it.
        """
        if req.path not in self._excluded_resources:
            # add a timestamp for call duration
            req.context['telemetry_timestamp'] = datetime.now()
            # TODO: add a log guid if it doesn't exist - separate middleware for this?
            # TODO: how to log the body
            self._info("Request received",
                       logCategory='apiRequest',
                       reqReferrer=', '.join(req.access_route),
                       reqVerb=req.method,
                       reqPath=req.path,
                       reqQuery=req.query_string,
                       reqBody='')

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
            except:
                pass # intentionally ignore

            duration = int((datetime.now() - req.context['telemetry_timestamp']).total_seconds() * 1000000)
            self._info("Request completed",
                       logCategory='apiResponse',
                       reqDurationMicros=duration,
                       reqStatusCode=status)