# -*- coding: utf-8 -*-
import falcon
from falcon import testing
import pytest
from unittest.mock import mock_open, call

from pprint import pprint

from app import app


@pytest.fixture
def client():
    return testing.TestClient(app)


# pytest will inject the object returned by the "client" function
# as an additional parameter.
def test_get_contacts(client):
    doc = {
        'images': [
            {
                'href': '/images/1eaf6ef1-7f2d-4ecc-a8d5-6e8adba7cc0e.png'
            }
        ]
    }

    response = client.simulate_get('/contacts')
    pprint(response)
    # result_doc = msgpack.unpackb(response.content, encoding='utf-8')

    # assert result_doc == doc
    assert response.status == falcon.HTTP_OK
