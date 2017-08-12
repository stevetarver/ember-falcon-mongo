import os
import falcon
import json
from typing import List, Dict
from pymongo import MongoClient, ReturnDocument
from pymongo import errors as pymongoErrors
from bson.objectid import ObjectId
from bson import errors as bsonErrors

from ..common.logging import LoggerMixin


class ContactsRepoMongo(LoggerMixin):
    """
    Handles all interactions with the MongoDB contacts collection

    NOTES:
    MongoDB bson ObjectIds are not json serializable, however, you can cast
    the ObjectId to a str, which is, and use that str to construct an ObjectId
    for searching.
    """

    def __init__(self):
        # 'mongodb://localhost:27017/'
        self._uri = os.getenv('MONGO_URI', '')
        if not self._uri:
            raise ValueError('MONGO_URI env var not set; required to connect to mongodb')
        self._mongo = MongoClient(self._uri,
                                     # Set the mongo connect timeout to 1s < gunicorn
                                     # worker timeout so we will fire a 503 when db is down
                                     serverSelectionTimeoutMS=29000)
        self._contacts = self._mongo.test.contacts

    # def create_item(self, req: falcon.Request):
    #     try:
    #         result = self._contacts.insert_one(
    #             json.load(req.bounded_stream)
    #         )
    #         return str(result.inserted_id)
    #     except (pymongoErrors.AutoReconnect, pymongoErrors.ConnectionFailure, pymongoErrors.NetworkTimeout):
    #         self._handle_service_unavailable()

    def delete_item(self, _: falcon.Request, object_id: str) -> None:
        try:
            self._contacts.delete_one(
                {'_id': self._make_objectid(object_id)}
            )
        except (pymongoErrors.AutoReconnect, pymongoErrors.ConnectionFailure, pymongoErrors.NetworkTimeout):
            self._handle_service_unavailable()

    def find_one(self) -> Dict:
        try:
            return self._contacts.find_one()
        except (pymongoErrors.AutoReconnect, pymongoErrors.ConnectionFailure, pymongoErrors.NetworkTimeout):
            self._handle_service_unavailable()

    def get_list(self, _: falcon.Request) -> List[Dict]:
        try:
            result = []
            for c in self._contacts.find():
                c['_id'] = str(c['_id'])
                result.append(c)
            return result
        except (pymongoErrors.AutoReconnect, pymongoErrors.ConnectionFailure, pymongoErrors.NetworkTimeout):
            self._handle_service_unavailable()

    def get_item(self, _: falcon.Request, object_id: str) -> Dict:
        try:
            contact = self._contacts.find_one(
                {'_id': self._make_objectid(object_id)}
            )
            if contact is None:
                self._handle_not_found(object_id)
            contact['_id'] = str(contact['_id'])
            return contact
        except (pymongoErrors.AutoReconnect, pymongoErrors.ConnectionFailure, pymongoErrors.NetworkTimeout):
            self._handle_service_unavailable()

    def ping(self) -> None:
        """
        A very light weight database connectivity check used with liveness and
        readiness probes. Throws a service unavailable exception on failure
        :return:
        """
        try:
            self._mongo.admin.command('ping')
        except:
            self._handle_service_unavailable()

    def replace_item(self, req: falcon.Request, object_id: str) -> Dict:
        try:
            result = self._contacts.find_one_and_replace(
                {'_id': self._make_objectid(object_id)},
                json.load(req.bounded_stream),
                return_document=ReturnDocument.AFTER)
            if result is None:
                self._handle_not_found(object_id)
            result['_id'] = str(result['_id'])
            return result
        except (pymongoErrors.AutoReconnect, pymongoErrors.ConnectionFailure, pymongoErrors.NetworkTimeout):
            self._handle_service_unavailable()

    def update_item(self, req: falcon.Request, object_id: str) -> Dict:
        try:
            result = self._contacts.find_one_and_update(
                {'_id': self._make_objectid(object_id)},
                {'$set': json.load(req.bounded_stream)},
                return_document=ReturnDocument.AFTER)
            if result is None:
                self._handle_not_found(object_id)
            result['_id'] = str(result['_id'])
            return result
        except (pymongoErrors.AutoReconnect, pymongoErrors.ConnectionFailure, pymongoErrors.NetworkTimeout):
            self._handle_service_unavailable()

    def _make_objectid(self, object_id: str) -> ObjectId:
        try:
            return ObjectId(object_id)
        except bsonErrors.InvalidId as ex:
            raise falcon.HTTPBadRequest(
                title='Invalid contact id: {}'.format(object_id),
                description=str(ex))

    def _handle_not_found(self, object_id) -> None:
        raise falcon.HTTPNotFound(
            title='Contact not found',
            description="Contact {} not found".format(object_id))

    def _handle_service_unavailable(self) -> None:
        raise falcon.HTTPServiceUnavailable(
            title='Datastore is unreachable',
            description="MongoDB at {} failed to respond to ping. "
                        "This is a transient, future attempts will work "
                        "when the datastore returns to service".format(self._uri),
            href='https://www.ctl.io/api-docs/v2/#firewall',
            retry_after=30
        )
