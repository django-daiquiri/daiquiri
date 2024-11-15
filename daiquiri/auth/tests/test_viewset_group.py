import pytest

from django.contrib.auth.models import Group
from django.urls import reverse

users = (
    ('admin', 'admin'),
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
        'admin': 405, 'manager': 403, 'user': 403, 'anonymous': 403
    },
    'update': {
        'admin': 405, 'manager': 403, 'user': 403, 'anonymous': 403
    },
    'delete': {
        'admin': 405, 'manager': 403, 'user': 403, 'anonymous': 403
    }
}

urlnames = {
    'list': 'auth:group-list',
    'detail': 'auth:group-detail'
}

instances = [10]


@pytest.mark.parametrize(('username', 'password'), users)
def test_list(db, client, username, password):
    client.login(username=username, password=password)

    url = reverse(urlnames['list'])
    response = client.get(url)
    assert response.status_code == status_map['list'][username], response.json()

    if response.status_code == 200:
        assert len(response.json()) == 7


@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('pk', instances)
def test_detail(db, client, username, password, pk):
    client.login(username=username, password=password)

    instance = Group.objects.get(pk=pk)

    url = reverse(urlnames['detail'], args=[pk])
    response = client.get(url)
    assert response.status_code == status_map['detail'][username], response.json()

    if response.status_code == 200:
        assert response.json().get('name') == instance.name


@pytest.mark.parametrize(('username', 'password'), users)
def test_create(db, client, username, password):
    client.login(username=username, password=password)

    url = reverse(urlnames['list'])
    response = client.post(url, {})
    assert response.status_code == status_map['create'][username], response.json()


@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('pk', instances)
def test_update(db, client, username, password, pk):
    client.login(username=username, password=password)

    url = reverse(urlnames['detail'], args=[pk])
    response = client.put(url, {}, content_type='application/json')
    assert response.status_code == status_map['update'][username], response.json()


@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('pk', instances)
def test_delete(db, client, username, password, pk):
    client.login(username=username, password=password)

    url = reverse(urlnames['detail'], args=[pk])
    response = client.delete(url)
    assert response.status_code == status_map['delete'][username], response.json()
