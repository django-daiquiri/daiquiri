import pytest

from django.urls import reverse

users = (
    ('admin', 'admin'),
    ('user', 'user'),
    ('anonymous', None),
)


@pytest.mark.parametrize(('username', 'password'), users)
def test_home(db, client, username, password):
    client.login(username=username, password=password)

    url = reverse('home')
    response = client.get(url)
    assert response.status_code == 200
