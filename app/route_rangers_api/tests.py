import pytest
from django.urls import reverse


def test_fake():
    assert 1 == 1


@pytest.mark.django_db
def test_hello_view(client):
    url = reverse("/map")

    response = client.get(url)
    import pdb

    pdb.set_trace()
    assert response.status_code == 200
