import pytest

from django.test import override_settings
from django.urls import reverse

users = (
    ('admin', 'admin'),
    ('manager', 'manager'),
    ('user', 'user'),
    ('anonymous', None),
)

status_map = {
    'query': {
        'admin': 200, 'manager': 200, 'user': 200, 'anonymous': 302
    },
    'examples': {
        'admin': 200, 'manager': 200, 'user': 403, 'anonymous': 302
    }
}


@pytest.mark.parametrize(('username', 'password'), users)
def test_query(db, client, username, password):
    client.login(username=username, password=password)

    url = reverse('query:query')
    response = client.get(url)
    assert response.status_code == status_map['query'][username]


@override_settings(QUERY_ANONYMOUS=True)
def test_list_anonymous(db, client):
    url = reverse('query:query')
    response = client.get(url)
    assert response.status_code == 200
