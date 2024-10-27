import pytest

from django.urls import reverse

from ..models import ContactMessage

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
    }
}

urlnames = {
    'list': 'contact:message-list',
    'detail': 'contact:message-detail'
}


instances = [1, 2]


@pytest.mark.parametrize(('username', 'password'), users)
def test_list(db, client, username, password):
    client.login(username=username, password=password)

    url = reverse(urlnames['list'])
    response = client.get(url)
    assert response.status_code == status_map['list'][username], response.json()

    if response.status_code == 200:
        assert response.json().get('count') == 2
        assert len(response.json().get('results')) == 2


@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('pk', instances)
def test_detail(db, client, username, password, pk):
    client.login(username=username, password=password)

    instance = ContactMessage.objects.get(pk=pk)
    url = reverse(urlnames['detail'], args=[pk])
    response = client.get(url)
    assert response.status_code == status_map['detail'][username], response.json()

    if response.status_code == 200:
        assert response.json().get('email') == instance.email


@pytest.mark.parametrize(('username', 'password'), users)
def test_create(db, client, username, password):
    client.login(username=username, password=password)

    url = reverse(urlnames['list'])
    response = client.post(url, {
        'author': 'Tanja Test',
        'email': 'test@example.com',
        'status': 'ACTIVE',
        'subject': 'Test',
        'message': 'This is a test.'
    })
    assert response.status_code == status_map['create'][username], response.json()


@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('pk', instances)
def test_update(db, client, username, password, pk):
    client.login(username=username, password=password)

    instance = ContactMessage.objects.get(pk=pk)
    instance_author = instance.author
    url = reverse(urlnames['detail'], args=[pk])
    response = client.put(url, {
        'author': 'Tanja Test',
        'email': 'test@example.com',
        'status': 'ACTIVE',
        'subject': 'Test',
        'message': 'This is a test.'
    }, content_type='application/json')
    assert response.status_code == status_map['update'][username], response.json()

    instance.refresh_from_db()
    assert instance.author == ('Tanja Test' if response.status_code == 200 else instance_author)


@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('pk', instances)
def test_delete(db, client, username, password, pk):
    client.login(username=username, password=password)

    url = reverse(urlnames['detail'], args=[pk])
    response = client.delete(url)
    assert response.status_code == status_map['delete'][username], response.json()
    assert ContactMessage.objects.filter(pk=pk).exists() is not (response.status_code == 204)
