import pytest
from django.urls import reverse
from route_rangers_api.models import TransitRoute


def test_fake():
    assert 1 == 1


@pytest.mark.django_db
def test_hello_view(client):
    url = reverse("/")

    response = client.get(url)
    assert response.status_code == 200
