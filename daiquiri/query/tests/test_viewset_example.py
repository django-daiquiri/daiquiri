import pytest

from django.test import override_settings
from django.urls import reverse

from ..models import Example

users = (
    ('admin', 'admin'),
    ('manager', 'manager'),
    ('user', 'user'),
    ('anonymous', None),
)

status_map = {
    'list': {
        'admin': 200, 'manager': 200, 'user': 403, 'anonymous': 403
    },
    'detail': {
        'admin': 200, 'manager': 200, 'user': 403, 'anonymous': 403
    },
    'create': {
        'admin': 201, 'manager': 201, 'user': 403, 'anonymous': 403
    },
    'update': {
        'admin': 200, 'manager': 200, 'user': 403, 'anonymous': 403
    },
    'delete': {
        'admin': 204, 'manager': 204, 'user': 403, 'anonymous': 403
    },
    'user': {
        'admin': 200, 'manager': 200, 'user': 200, 'anonymous': 403
    }
}

urlnames = {
    'list': 'query:example-list',
    'detail': 'query:example-detail',
    'user': 'query:example-user',
}

instances = [1]


@pytest.mark.parametrize(('username', 'password'), users)
def test_list(db, client, username, password):
    client.login(username=username, password=password)

    url = reverse(urlnames['list'])
    response = client.get(url)
    assert response.status_code == status_map['list'][username], response.json()

    if response.status_code == 200:
        assert response.json()['count'] == 4
        assert response.json()['results'][0]['access_level'] == 'PUBLIC'


@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('pk', instances)
def test_detail(db, client, username, password, pk):
    client.login(username=username, password=password)

    instance = Example.objects.get(pk=pk)
    url = reverse(urlnames['detail'], args=[pk])
    response = client.get(url)
    assert response.status_code == status_map['detail'][username], response.json()

    if response.status_code == 200:
        assert response.json().get('access_level') == instance.access_level


@pytest.mark.parametrize(('username', 'password'), users)
def test_create(db, client, mocker, username, password):
    client.login(username=username, password=password)

    url = reverse(urlnames['list'])
    response = client.post(url, {
        'name': 'Test',
        'query_string': 'SELECT foo FROM bar',
        'access_level': 'PUBLIC',
        'query_language': 'adql-2.0'
    })
    assert response.status_code == status_map['create'][username], response.json()


@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('pk', instances)
def test_update(db, client, mocker, username, password, pk):
    client.login(username=username, password=password)

    instance = Example.objects.get(pk=pk)
    instance_name = instance.name
    url = reverse(urlnames['detail'], args=[pk])
    response = client.put(url, {
        'name': 'Test',
        'query_string': 'SELECT foo FROM bar',
        'access_level': 'PUBLIC',
        'query_language': 'adql-2.0'
    }, content_type='application/json')
    assert response.status_code == status_map['update'][username], response.json()

    instance.refresh_from_db()
    assert instance.name == ('Test' if response.status_code == 200 else instance_name)


@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('pk', instances)
def test_delete(db, client, mocker, username, password, pk):
    client.login(username=username, password=password)

    url = reverse(urlnames['detail'], args=[pk])
    response = client.delete(url)
    assert response.status_code == status_map['delete'][username], response.json()
    assert Example.objects.filter(pk=pk).exists() is not (response.status_code == 204)


@pytest.mark.parametrize(('username', 'password'), users)
def test_user(db, client, username, password):
    client.login(username=username, password=password)

    url = reverse(urlnames['user'])
    response = client.get(url)
    assert response.status_code == status_map['user'][username], response.json()

    if response.status_code == 200:
        assert len(response.json()) == (3 if username == 'admin' else 2)
        assert response.json()[0]['id'] == 1


@override_settings(QUERY_ANONYMOUS=True)
def test_user_anonymous(db, client):
    url = reverse(urlnames['user'])
    response = client.get(url)
    assert response.status_code == 200, response.json()

    if response.status_code == 200:
        assert len(response.json()) == 1
        assert response.json()[0]['id'] == 1
