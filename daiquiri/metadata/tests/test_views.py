import pytest

from django.urls import reverse

users = (
    ('admin', 'admin'),
    ('manager', 'manager'),
    ('user', 'user'),
    ('test', 'test'),
    ('anonymous', None),
)

status_map = {
    'management': {
        'admin': 200, 'manager': 200, 'user': 403, 'test': 403, 'anonymous': 302
    },
    'public_schema': {
        'admin': 200, 'manager': 200, 'user': 200, 'test': 200, 'anonymous': 200
    },
    'internal_schema': {
        'admin': 200, 'manager': 200, 'user': 200, 'test': 200, 'anonymous': 404
    },
    'private_schema': {
        'admin': 404, 'manager': 404, 'user': 404, 'test': 200, 'anonymous': 404
    },
    'public_table': {
        'admin': 200, 'manager': 200, 'user': 200, 'test': 200, 'anonymous': 200
    },
    'internal_table': {
        'admin': 200, 'manager': 200, 'user': 200, 'test': 200, 'anonymous': 404
    },
    'private_table': {
        'admin': 404, 'manager': 404, 'user': 404, 'test': 200, 'anonymous': 404
    }
}


@pytest.mark.parametrize(('username', 'password'), users)
def test_management(db, client, username, password):
    client.login(username=username, password=password)

    url = reverse('metadata:management')
    response = client.get(url)
    assert response.status_code == status_map['management'][username]


@pytest.mark.parametrize(('username', 'password'), users)
def test_public_schema(db, client, username, password):
    client.login(username=username, password=password)

    url = reverse('metadata:schema', kwargs={
        'schema_name': 'daiquiri_data_obs'
    })
    response = client.get(url)
    assert response.status_code == status_map['public_schema'][username]


@pytest.mark.parametrize(('username', 'password'), users)
def test_internal_schema(db, client, username, password):
    client.login(username=username, password=password)

    url = reverse('metadata:schema', kwargs={
        'schema_name': 'daiquiri_data_sim'
    })
    response = client.get(url)
    assert response.status_code == status_map['internal_schema'][username]


@pytest.mark.parametrize(('username', 'password'), users)
def test_private_schema(db, client, username, password):
    client.login(username=username, password=password)

    url = reverse('metadata:schema', kwargs={
        'schema_name': 'daiquiri_data_test'
    })
    response = client.get(url)
    assert response.status_code == status_map['private_schema'][username]


@pytest.mark.parametrize(('username', 'password'), users)
def test_public_table(db, client, username, password):
    client.login(username=username, password=password)

    url = reverse('metadata:table', kwargs={
        'schema_name': 'daiquiri_data_obs',
        'table_name': 'stars'
    })
    response = client.get(url)
    assert response.status_code == status_map['public_table'][username]


@pytest.mark.parametrize(('username', 'password'), users)
def test_internal_table(db, client, username, password):
    client.login(username=username, password=password)

    url = reverse('metadata:table', kwargs={
        'schema_name': 'daiquiri_data_sim',
        'table_name': 'halos'
    })
    response = client.get(url)
    assert response.status_code == status_map['internal_table'][username]


@pytest.mark.parametrize(('username', 'password'), users)
def test_private_table(db, client, username, password):
    client.login(username=username, password=password)

    url = reverse('metadata:table', kwargs={
        'schema_name': 'daiquiri_data_test',
        'table_name': 'test'
    })
    response = client.get(url)
    assert response.status_code == status_map['private_table'][username]
