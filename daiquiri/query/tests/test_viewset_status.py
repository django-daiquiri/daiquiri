import pytest

from django.test import override_settings
from django.urls import reverse

users = (
    ('admin', 'admin'),
    ('user', 'user'),
    ('evil', 'evil'),
    ('anonymous', None),
)

status_map = {
    'list': {
        'admin': 200, 'user': 200, 'evil': 200, 'anonymous': 403
    }
}

urlnames = {
    'list': 'query:status-list'
}


@pytest.mark.parametrize(('username', 'password'), users)
def test_list(db, client, username, password):
    client.login(username=username, password=password)

    url = reverse(urlnames['list'])
    response = client.get(url)
    assert response.status_code == status_map['list'][username], response.json()

    if response.status_code == 200:
        assert response.json().get('guest') is False


@override_settings(QUERY_ANONYMOUS=True)
def test_list_anonymous(db, client):
    url = reverse(urlnames['list'])
    response = client.get(url)
    assert response.status_code == 200, response.json()

    if response.status_code == 200:
        assert response.json().get('guest') is True
