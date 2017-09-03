# -*- coding: utf-8 -*-
"""
json:api helpers

see http://jsonapi.org/
"""
import json
from typing import Union, Dict, List


def make_response(data_type: str, id_key: str, data: Union[Dict, List[Dict]]) -> str:
    """
    Format a normal response body IAW json:api.

    A proper, minimal, response body looks like::

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

    Args:
        data_type (str): generic type name of data, e.g "contacts"
        id_key (str): key name in data that holds the id value
        data (dict or list(dict)): a response object or list

    Returns:
        str: JSON string respresentation for the response body
    """
    if isinstance(data, list):
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
