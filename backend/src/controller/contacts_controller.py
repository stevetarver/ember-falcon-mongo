import falcon
from typing import List, Dict

from ..common.logging import LoggerMixin
from ..repository.contacts_repository import ContactsRepoMongo


class ContactsController(LoggerMixin):
    """
    Controllers orchestrate calls to other controllers and repositories
    to complete API requests.
    """

    def __init__(self):
        self._repo = ContactsRepoMongo()

    # def create_item(self, req: falcon.Request):
    #     return self._repo.create_item(req)

    def delete_item(self, req: falcon.Request, id: str) -> None:
        self._repo.delete_item(req, id)

    def find_one(self) -> Dict:
        return self._repo.find_one()

    def get_list(self, req: falcon.Request) -> List[Dict]:
        return self._repo.get_list(req)

    def get_item(self, req: falcon.Request, id: str) -> Dict:
        return self._repo.get_item(req, id)

    def update_item(self, req: falcon.Request, id: str) -> Dict:
        return self._repo.update_item(req, id)

    def replace_item(self, req: falcon.Request, id: str) -> Dict:
        return self._repo.replace_item(req, id)