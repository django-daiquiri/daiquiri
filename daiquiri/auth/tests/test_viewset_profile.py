import pytest

from django.urls import reverse

from ..models import Profile

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
        'admin': 405, 'manager': 403, 'user': 403, 'anonymous': 403
    },
    'update': {
        'admin': 200, 'manager': 200, 'user': 403, 'anonymous': 403
    },
    'delete': {
        'admin': 405, 'manager': 403, 'user': 403, 'anonymous': 403
    },
    'confirm': {
        'admin': 200, 'manager': 200, 'user': 403, 'anonymous': 403
    },
    'reject': {
        'admin': 200, 'manager': 200, 'user': 403, 'anonymous': 403
    },
    'activate': {
        'admin': 200, 'manager': 200, 'user': 403, 'anonymous': 403
    },
    'disable': {
        'admin': 200, 'manager': 200, 'user': 403, 'anonymous': 403
    },
    'enable': {
        'admin': 200, 'manager': 200, 'user': 403, 'anonymous': 403
    }
}

urlnames = {
    'list': 'auth:profile-list',
    'detail': 'auth:profile-detail',
    'confirm': 'auth:profile-confirm',
    'reject': 'auth:profile-reject',
    'activate': 'auth:profile-activate',
    'enable': 'auth:profile-enable',
    'disable': 'auth:profile-disable'
}

instances = [5]


@pytest.mark.parametrize(('username', 'password'), users)
def test_list(db, client, username, password):
    client.login(username=username, password=password)

    url = reverse(urlnames['list'])
    response = client.get(url)
    assert response.status_code == status_map['list'][username], response.json()

    if response.status_code == 200:
        assert len(response.json()) == 4


@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('pk', instances)
def test_detail(db, client, username, password, pk):
    client.login(username=username, password=password)

    instance = Profile.objects.get(pk=pk)

    url = reverse(urlnames['detail'], args=[pk])
    response = client.get(url)
    assert response.status_code == status_map['detail'][username], response.json()

    if response.status_code == 200:
        assert response.json().get('user').get('username') == instance.user.username


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

    instance = Profile.objects.get(pk=pk)
    instance_first_name = instance.user.first_name

    url = reverse(urlnames['detail'], args=[pk])
    response = client.put(url, {
        'attributes': instance.attributes,
        'details': instance.details,
        'user': {
            'first_name': 'Test',
            'last_name': instance.user.last_name,
            'groups': [group.id for group in instance.user.groups.all()],
        }
    }, content_type='application/json')
    assert response.status_code == status_map['update'][username], response.json()

    instance.refresh_from_db()
    assert instance.user.first_name == ('Test' if response.status_code == 200 else instance_first_name)


@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('pk', instances)
def test_delete(db, client, username, password, pk):
    client.login(username=username, password=password)

    url = reverse(urlnames['detail'], args=[pk])
    response = client.delete(url)
    assert response.status_code == status_map['delete'][username], response.json()
    assert Profile.objects.filter(pk=pk).exists() is True


@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('pk', instances)
def test_confirm(db, client, username, password, pk):
    client.login(username=username, password=password)

    instance = Profile.objects.get(pk=pk)
    instance.is_pending = True
    instance.is_confirmed = False
    instance.user.save()
    instance.save()

    url = reverse(urlnames['confirm'], args=[pk])
    response = client.put(url)
    assert response.status_code == status_map['confirm'][username], response.json()

    instance.refresh_from_db()
    assert instance.is_pending is True
    assert instance.is_confirmed == (response.status_code == 200)
    assert instance.user.is_active is True


@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('pk', instances)
def test_reject(db, client, username, password, pk):
    client.login(username=username, password=password)

    instance = Profile.objects.get(pk=pk)
    instance.is_pending = True
    instance.is_confirmed = False
    instance.user.is_active = True
    instance.user.save()
    instance.save()

    url = reverse(urlnames['reject'], args=[pk])
    response = client.put(url)
    assert response.status_code == status_map['reject'][username], response.json()

    instance.refresh_from_db()
    assert instance.is_pending is not (response.status_code == 200)
    assert instance.is_confirmed is False
    assert instance.user.is_active is not (response.status_code == 200)


@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('pk', instances)
def test_activate(db, client, username, password, pk):
    client.login(username=username, password=password)

    instance = Profile.objects.get(pk=pk)
    instance.is_pending = True
    instance.is_confirmed = False
    instance.user.save()
    instance.save()

    url = reverse(urlnames['activate'], args=[pk])
    response = client.put(url)
    assert response.status_code == status_map['activate'][username], response.json()

    instance.refresh_from_db()
    assert instance.is_pending is not (response.status_code == 200)
    assert instance.is_confirmed is (response.status_code == 200)
    assert instance.user.is_active is True


@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('pk', instances)
def test_enable(db, client, username, password, pk):
    client.login(username=username, password=password)

    instance = Profile.objects.get(pk=pk)
    instance.user.is_active = False
    instance.user.save()

    url = reverse(urlnames['enable'], args=[pk])
    response = client.put(url)
    assert response.status_code == status_map['enable'][username], response.json()

    instance.refresh_from_db()
    assert instance.is_pending is False
    assert instance.is_confirmed is False
    assert instance.user.is_active is (response.status_code == 200)


@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('pk', instances)
def test_disable(db, client, username, password, pk):
    client.login(username=username, password=password)

    instance = Profile.objects.get(pk=pk)

    url = reverse(urlnames['disable'], args=[pk])
    response = client.put(url)
    assert response.status_code == status_map['disable'][username], response.json()

    instance.refresh_from_db()
    assert instance.is_pending is False
    assert instance.is_confirmed is False
    assert instance.user.is_active is not (response.status_code == 200)
