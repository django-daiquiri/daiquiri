from urllib.parse import urlencode

import pytest

from django.urls import reverse

users = (
    ('admin', 'admin'),
    ('user', 'user'),
    ('test', 'test'),
    ('anonymous', None),
)


@pytest.mark.parametrize(('username', 'password'), users)
def test_public_row_list(db, client, username, password):
    client.login(username=username, password=password)

    url = reverse('serve:row-list') + '?' + urlencode({
        'schema': 'daiquiri_data_obs',
        'table': 'stars'
    })
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.parametrize(('username', 'password'), users)
def test_internal_row_list(db, client, username, password):
    client.login(username=username, password=password)

    url = reverse('serve:row-list') + '?' + urlencode({
        'schema': 'daiquiri_data_sim',
        'table': 'halos'
    })
    response = client.get(url)
    assert response.status_code == 404 if username == 'anonymous' else 200


@pytest.mark.parametrize(('username', 'password'), users)
def test_private_row_list(db, client, username, password):
    client.login(username=username, password=password)

    url = reverse('serve:row-list') + '?' + urlencode({
        'schema': 'daiquiri_data_test',
        'table': 'test'
    })
    response = client.get(url)
    assert response.status_code == 200 if username == 'test' else 404


@pytest.mark.parametrize(('username', 'password'), users)
def test_non_existing_schema_row_list(db, client, username, password):
    client.login(username=username, password=password)

    url = reverse('serve:row-list') + '?' + urlencode({
        'schema': 'non_existing',
        'table': 'stars'
    })
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.parametrize(('username', 'password'), users)
def test_non_existing_table_row_list(db, client, username, password):
    client.login(username=username, password=password)

    url = reverse('serve:row-list') + '?' + urlencode({
        'schema': 'daiquiri_data_obs',
        'table': 'non_existing'
    })
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.parametrize(('username', 'password'), users)
def test_non_existing_user_table_row_list(db, client, username, password):
    client.login(username=username, password=password)

    url = reverse('serve:row-list') + '?' + urlencode({
        'schema': 'daiquiri_user_user',
        'table': 'non_existing'
    })
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.parametrize(('username', 'password'), users)
def test_public_column_list(db, client, username, password):
    client.login(username=username, password=password)

    url = reverse('serve:column-list') + '?' + urlencode({
        'schema': 'daiquiri_data_obs',
        'table': 'stars'
    })
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.parametrize(('username', 'password'), users)
def test_internal_column_list(db, client, username, password):
    client.login(username=username, password=password)

    url = reverse('serve:column-list') + '?' + urlencode({
        'schema': 'daiquiri_data_sim',
        'table': 'halos'
    })
    response = client.get(url)
    assert response.status_code == 404 if username == 'anonymous' else 200


@pytest.mark.parametrize(('username', 'password'), users)
def test_private_column_list(db, client, username, password):
    client.login(username=username, password=password)

    url = reverse('serve:column-list') + '?' + urlencode({
        'schema': 'daiquiri_data_test',
        'table': 'test'
    })
    response = client.get(url)
    assert response.status_code == 200 if username == 'test' else 404


@pytest.mark.parametrize(('username', 'password'), users)
def test_non_existing_schema_column_list(db, client, username, password):
    client.login(username=username, password=password)

    url = reverse('serve:column-list') + '?' + urlencode({
        'schema': 'non_existing',
        'table': 'stars'
    })
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.parametrize(('username', 'password'), users)
def test_non_existing_table_column_list(db, client, username, password):
    client.login(username=username, password=password)

    url = reverse('serve:column-list') + '?' + urlencode({
        'schema': 'daiquiri_data_obs',
        'table': 'non_existing'
    })
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.parametrize(('username', 'password'), users)
def test_non_existing_user_table_column_list(db, client, username, password):
    client.login(username=username, password=password)

    url = reverse('serve:column-list') + '?' + urlencode({
        'schema': 'daiquiri_user_user',
        'table': 'non_existing'
    })
    response = client.get(url)
    assert response.status_code == 404
