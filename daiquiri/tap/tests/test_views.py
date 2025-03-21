import pytest

from django.urls import reverse

users = (
    ('admin', 'admin'),
    ('user', 'user'),
    ('anonymous', None),
)


@pytest.mark.parametrize(('username', 'password'), users)
def test_root(db, client, username, password):
    client.login(username=username, password=password)

    url = reverse('tap:root')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.parametrize(('username', 'password'), users)
def test_availability(db, client, username, password):
    client.login(username=username, password=password)

    url = reverse('tap:availability')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.parametrize(('username', 'password'), users)
def test_capabilities(db, client, username, password):
    client.login(username=username, password=password)

    url = reverse('tap:capabilities')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.parametrize(('username', 'password'), users)
def test_tables(db, client, username, password):
    client.login(username=username, password=password)

    url = reverse('tap:tables')
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.parametrize(('username', 'password'), users)
def test_examples(db, client, username, password):
    client.login(username=username, password=password)

    url = reverse('tap:examples')
    response = client.get(url)
    assert response.status_code == 200
