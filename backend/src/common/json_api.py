from typing import Union, Dict, List
import json


def make_response(data_type: str, id_key: str, data: Union[Dict, List[Dict]]) -> str:
    """
    Format a normal response body IAW json:api.

    A common response body looks like:
        {
        "data": {
            "type": "contacts"
            "id": "5973ecc8c453c823e4c471d2",
            "attributes": {
                "_id": "5973ecc8c453c823e4c471d2",
                "address": "89992 E 15th St",
                ...
                },
            }
        }
    Note: the passed data ends up in the attributes section of the json:api data object

    :param data_type: generic type of data, e.g "contacts"
    :param id_key: key name in data that holds the id value
    :param data: and object or list of objects containing response data
    :return: JSON string respresentation for the response body
    """
    result = None
    if type(data) is list:
        items = []
        for item in data:
            items.append(_make_response_item(data_type, id_key, item))
        result = dict(data=items)
    else:
        result = dict(data=_make_response_item(data_type, id_key, data))
    return json.dumps(result, ensure_ascii=False)


def _make_response_item(data_type: str, id_key: str, data: Dict) -> dict:
    return dict(
        type=data_type,
        id=data[id_key],
        attributes=data,
    )
