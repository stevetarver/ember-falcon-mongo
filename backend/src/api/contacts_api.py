# -*- coding: utf-8 -*-
from typing import Union, List, Dict
import falcon

from ..common.logging import LoggerMixin
from ..common.json_api import make_response
from ..controller.contacts_controller import ContactsController

"""
Contacts API

Falcon wants a single class as a responder for each URI. Most frequently,
this will divide a single resource into operations on the collection and
collection items. We use:
    - Contacts: for operations on the entire contacts collection
    - Contact: for operations on a single contact item

ReST API classes
Classes in the api directory are responsible for
    - request parameter validation
    - response encoding
    - exception handling

Logging
Each class is subclassed from the LoggerMixin which exposes protected
members for logging. The logging mixins add information about the class
to the log entry.
"""


class _ContactsApi(LoggerMixin):

    def __init__(self):
        self._controller = ContactsController()

    def _validate_contact(req: falcon.Request, resp: falcon.Response, resource, params):
        """
        Validate create contact params.
        This will normally be attached to the on_post, on_put methods via a before hook.
                @falcon.before(_ContactsApi._validate_contact)

        :param req:
        :param resp:
        :param resource:
        :param params:
        :return:
        """
        # perform validation and if failure ->
        msg = 'Image type not allowed. Must be PNG, JPEG, or GIF'
        raise falcon.HTTPBadRequest('Bad request', msg)

    def _make_response(self, data: Union[Dict, List[Dict]]) -> str:
        """ Return JSON respresentation for the data object """
        return make_response('contacts', '_id', data)


class ContactsApi(_ContactsApi):

    def on_get(self, req: falcon.Request, resp: falcon.Response) -> None:
        data = self._controller.get_list(req)
        resp.body = self._make_response(data)

    # def on_post(self, req: falcon.Request, resp: falcon.Response):
    #     object_id = self._controller.create_item(req)
    #     resp.body = dict(
    #             type='contacts',
    #             id=object_id,
    #             attributes=dict(_id=object_id),
    #         )


class ContactApi(_ContactsApi):

    def on_delete(self, req: falcon.Request, _: falcon.Response, id: str) -> None:
        self._controller.delete_item(req, id)

    def on_get(self, req: falcon.Request, resp: falcon.Response, id: str) -> None:
        data = self._controller.get_item(req, id)
        resp.body = self._make_response(data)

    def on_patch(self, req: falcon.Request, resp: falcon.Response, id: str) -> None:
        data = self._controller.update_item(req, id)
        resp.body = self._make_response(data)

    def on_put(self, req: falcon.Request, resp: falcon.Response, id: str) -> None:
        data = self._controller.replace_item(req, id)
        resp.body = self._make_response(data)





