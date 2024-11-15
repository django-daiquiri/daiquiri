import pytest

from django.urls import reverse

users = (
    ('admin', 'admin'),
    ('user', 'user'),
    ('test', 'test'),
    ('anonymous', None),
)


@pytest.mark.parametrize(('username', 'password'), users)
def test_public_table(db, client, username, password):
    client.login(username=username, password=password)

    url = reverse('serve:table', kwargs={
        'schema_name': 'daiquiri_data_obs',
        'table_name': 'stars'
    })
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.parametrize(('username', 'password'), users)
def test_internal_table(db, client, username, password):
    client.login(username=username, password=password)

    url = reverse('serve:table', kwargs={
        'schema_name': 'daiquiri_data_sim',
        'table_name': 'halos'
    })
    response = client.get(url)
    assert response.status_code == 404 if username == 'anonymous' else 200


@pytest.mark.parametrize(('username', 'password'), users)
def test_private_table(db, client, username, password):
    client.login(username=username, password=password)

    url = reverse('serve:table', kwargs={
        'schema_name': 'daiquiri_data_test',
        'table_name': 'test'
    })
    response = client.get(url)
    assert response.status_code == 200 if username == 'test' else 404


@pytest.mark.parametrize(('username', 'password'), users)
def test_non_existing_schema(db, client, username, password):
    client.login(username=username, password=password)

    url = reverse('serve:table', kwargs={
        'schema_name': 'non_existing',
        'table_name': 'stars'
    })
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.parametrize(('username', 'password'), users)
def test_non_existing_table(db, client, username, password):
    client.login(username=username, password=password)

    url = reverse('serve:table', kwargs={
        'schema_name': 'daiquiri_data_obs',
        'table_name': 'non_existing'
    })
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.parametrize(('username', 'password'), users)
def test_non_existing_user_table(db, client, username, password):
    client.login(username=username, password=password)

    url = reverse('serve:table', kwargs={
        'schema_name': 'daiquiri_user_user',
        'table_name': 'non_existing'
    })
    response = client.get(url)
    assert response.status_code == 404
