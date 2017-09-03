# -*- coding: utf-8 -*-
"""
Orchestration for operations on the contacts collection.

This is simply pass-through now, but left as a place-holder as an
example of a more robust service.
"""
from typing import List, Dict

import falcon

from ..common.logging import LoggerMixin
from ..repository.contacts_repository import ContactsRepoMongo


class ContactsController(LoggerMixin):
    """
    Controllers orchestrate calls to other controllers and repositories
    to complete API requests.
    """
    def __init__(self):
        self._repo = ContactsRepoMongo()

    def create_item(self, req: falcon.Request):
        return self._repo.create_item(req)

    def delete_item(self, req: falcon.Request, contact_id: str) -> None:
        self._repo.delete_item(req, contact_id)

    def find_one(self) -> Dict:
        return self._repo.find_one()

    def get_list(self, req: falcon.Request) -> List[Dict]:
        return self._repo.get_list(req)

    def get_item(self, req: falcon.Request, contact_id: str) -> Dict:
        return self._repo.get_item(req, contact_id)

    def update_item(self, req: falcon.Request, contact_id: str) -> Dict:
        return self._repo.update_item(req, contact_id)

    def replace_item(self, req: falcon.Request, contact_id: str) -> Dict:
        return self._repo.replace_item(req, contact_id)
