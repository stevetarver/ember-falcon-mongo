# -*- coding: utf-8 -*-
"""
Application entry point.

Initializes the application and returns a falcon.API for Gunicorn to run.

Example::

    PYTHONPATH=$PYTHONPATH:. \
    MONGO_URI='mongodb://localhost:27017/' \
    gunicorn \
        --workers 5 \
        --logger-class app.common.logging.GunicornLogger \
        'app.app:run()'
"""
import falcon

from .api.contacts_api import ContactsApi, ContactApi
from .api.health import Liveness, Readiness, Ping
from .common.falcon_mods import falcon_error_serializer
from .common.logging import Logger
from .common.middleware import Telemetry


def initialize() -> falcon.API:
    """
    Initialize the falcon api and our router
    """
    # No need to initialize logging here - Gunicorn will do it and then load us
    # into a configured system
    # initialize_logging()

    # Create our WSGI application
    # media_type set for json:api compliance
    api = falcon.API(media_type='application/vnd.api+json',
                     middleware=[Telemetry()])

    # Add a json:api compliant error serializer
    api.set_error_serializer(falcon_error_serializer)

    # Routes
    api.add_route('/contacts', ContactsApi())
    api.add_route('/contacts/{contact_id}', ContactApi())
    api.add_route('/liveness', Liveness())
    api.add_route('/ping', Ping())
    api.add_route('/readiness', Readiness())
    return api


def run() -> falcon.API:
    """
    :return: an initialized falcon.API
    """
    Logger('app').info("ember-falcon-mongo service starting")
    return initialize()
