import pytest

from django.urls import reverse

users = (
    ('admin', 'admin'),
    ('manager', 'manager'),
    ('user', 'user'),
    ('anonymous', None),
)

status_map = {
    'users': {
        'admin': 200, 'manager': 200, 'user': 403, 'anonymous': 302
    }
}


@pytest.mark.parametrize(('username', 'password'), users)
def test_users(db, client, username, password):
    client.login(username=username, password=password)

    url = reverse('auth:users')
    response = client.get(url)
    assert response.status_code == status_map['users'][username]
