import falcon
from datetime import datetime

from ..common.json_api import make_response
from ..controller.contacts_controller import ContactsController
from ..repository.contacts_repository import ContactsRepoMongo


class Liveness(object):
    """
    Are we functional? Or should our scheduler kill us and make another.

    We will pump a get message through our service to prove all parts viable

    Return 200 OK if we are functional, 503 otherwise.
    """
    def on_get(self, _: falcon.Request, resp: falcon.Response):
        start = datetime.now()
        _ = ContactsController().find_one()
        duration = int((datetime.now() - start).total_seconds() * 1000000)

        resp.body = make_response('liveness',
                                  'id',
                                  dict(id=0,
                                       mongodb='ok',
                                       mongodbFindOneDurationMicros=duration))


class Readiness(object):
    """
    Are we ready to serve requests?

    Check that we can connect to all upstream components.

    Return 200 OK if we are functional, 503 otherwise.
    """
    def on_get(self, _: falcon.Request, resp: falcon.Response):
        start = datetime.now()
        ContactsRepoMongo().ping()
        duration = int((datetime.now() - start).total_seconds() * 1000000)

        resp.body = make_response('readiness',
                                  'id',
                                  dict(id=0,
                                       mongodb='ok',
                                       mongodbPingDurationMicros=duration))


class Ping(object):
    """
    Can someone connect to us?

    Light weight connectivity test for other service's liveness and readiness probes.

    Return 200 OK if we got this far, framework will fail or not respond
    otherwise
    """
    def on_get(self, _: falcon.Request, resp: falcon.Response):
        resp.body = make_response('ping',
                                  'id',
                                  dict(id=0))

