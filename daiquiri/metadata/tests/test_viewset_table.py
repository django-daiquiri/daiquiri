from urllib.parse import urlencode

import pytest

from django.urls import reverse

from ..models import Table

users = (
    ('admin', 'admin'),
    ('manager', 'manager'),
    ('user', 'user'),
    ('test', 'test'),
    ('anonymous', None),
)

status_map = {
    'list': {
        'admin': 200, 'manager': 200, 'user': 403, 'test': 403, 'anonymous': 403
    },
    'detail': {
        'admin': 200, 'manager': 200, 'user': 403, 'test': 403, 'anonymous': 403
    },
    'create': {
        'admin': 201, 'manager': 201, 'user': 403, 'test': 403, 'anonymous': 403
    },
    'update': {
        'admin': 200, 'manager': 200, 'user': 403, 'test': 403, 'anonymous': 403
    },
    'delete': {
        'admin': 204, 'manager': 204, 'user': 403, 'test': 403, 'anonymous': 403
    },
    'discover': {
        'admin': 200, 'manager': 200, 'user': 403, 'test': 403, 'anonymous': 403
    }
}

urlnames = {
    'list': 'metadata:table-list',
    'detail': 'metadata:table-detail',
    'discover': 'metadata:table-discover'
}

instances = [3]


@pytest.mark.parametrize(('username', 'password'), users)
def test_list(db, client, username, password):
    client.login(username=username, password=password)

    url = reverse(urlnames['list'])
    response = client.get(url)
    assert response.status_code == status_map['list'][username], response.json()

    if response.status_code == 200:
        assert len(response.json()) == 8


@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('pk', instances)
def test_detail(db, client, username, password, pk):
    client.login(username=username, password=password)

    instance = Table.objects.get(pk=pk)
    url = reverse(urlnames['detail'], args=[pk])
    response = client.get(url)
    assert response.status_code == status_map['detail'][username], response.json()

    if response.status_code == 200:
        assert response.json().get('name') == instance.name


@pytest.mark.parametrize(('username', 'password'), users)
def test_create(db, client, username, password):
    client.login(username=username, password=password)

    url = reverse(urlnames['list'])
    response = client.post(url, {
        'schema': 3,
        'name': 'test',
        'discover': True
    })
    assert response.status_code == status_map['create'][username], response.json()


@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('pk', instances)
def test_update(db, client, username, password, pk):
    client.login(username=username, password=password)

    instance = Table.objects.get(pk=pk)
    instance_name = instance.name
    url = reverse(urlnames['detail'], args=[pk])
    response = client.put(url, {
        'schema': 3,
        'name': 'test',
    }, content_type='application/json')
    assert response.status_code == status_map['update'][username], response.json()

    instance.refresh_from_db()
    assert instance.name == ('test' if response.status_code == 200 else instance_name)


@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('pk', instances)
def test_delete(db, client, username, password, pk):
    client.login(username=username, password=password)

    url = reverse(urlnames['detail'], args=[pk])
    response = client.delete(url)
    assert response.status_code == status_map['delete'][username], response.json()
    assert Table.objects.filter(pk=pk).exists() is not (response.status_code == 204)


@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('pk', instances)
def test_discover(db, client, username, password, pk):
    client.login(username=username, password=password)

    url = reverse(urlnames['discover'], args=[pk])
    response = client.post(url)
    assert response.status_code == status_map['discover'][username], response.json()
