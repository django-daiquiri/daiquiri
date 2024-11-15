from pathlib import Path
from unittest import mock

import pytest

from django.conf import settings
from django.test import override_settings
from django.urls import reverse

from ..models import QueryJob

users = (
    ('admin', 'admin'),
    ('user', 'user'),
    ('test', 'test'),
    ('evil', 'evil'),
    ('anonymous', None),
)

status_map = {
    'list': {
        'admin': 200, 'user': 200, 'test': 200, 'evil': 200, 'anonymous': 403
    },
    'detail': {
        'admin': 404, 'user': 200, 'test': 404, 'evil': 404, 'anonymous': 403
    },
    'create_internal': {
        'admin': 201, 'user': 201, 'test': 201, 'evil': 201, 'anonymous': 403
    },
    'create_private': {
        'admin': 400, 'user': 400, 'test': 201, 'evil': 400, 'anonymous': 403
    },
    'update': {
        'admin': 404, 'user': 200, 'test': 404, 'evil': 404, 'anonymous': 403
    },
    'delete': {
        'admin': 404, 'user': 204, 'test': 404, 'evil': 404, 'anonymous': 403
    }
}

urlnames = {
    'list': 'query:job-list',
    'detail': 'query:job-detail',
    'abort': 'query:job-abort',
    'create-download': 'query:job-create-download',
    'download': 'query:job-download',
    'stream': 'query:job-stream',
    'rows': 'query:job-rows',
    'columns': 'query:job-columns'
}

instances = [
    '679b5ce8-bbcf-41c2-ba45-2340910bcfae',
    '5527f2b0-7130-466d-b8d2-dbf6c5f700bf',
    'c87926e4-8e5f-4032-a764-826b6a39c171',
    '1b6c93ef-4161-4402-b1a7-d1237657e807'
]

public_queries = [
    'SELECT ra, dec, parallax, id FROM daiquiri_data_obs.stars'
]

internal_queries = [
    'SELECT ra, dec, parallax, id FROM daiquiri_data_obs.stars',
    'SELECT x, y, z, vx, vy, vz, id FROM daiquiri_data_sim.halos'
]

private_queries = [
    'SELECT id, "bool", "array", matrix FROM daiquiri_data_test.test'
]

format_keys = ('votable', 'csv', 'fits')


@pytest.mark.parametrize(('username', 'password'), users)
def test_list(db, client, username, password):
    client.login(username=username, password=password)

    url = reverse(urlnames['list'])
    response = client.get(url)
    assert response.status_code == status_map['list'][username], response.json()

    if response.status_code == 200:
        if username == 'user':
            assert response.json()['count'] == 4
            assert response.json()['results'][0]['table_name'] == 'test_pending'
        else:
            assert response.json()['count'] == 0


@override_settings(QUERY_ANONYMOUS=True)
def test_list_anonymous(db, client):
    url = reverse(urlnames['list'])
    response = client.get(url)
    assert response.status_code == 200, response.json()

    if response.status_code == 200:
        assert response.json()['count'] == 0


@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('pk', instances)
def test_detail(db, client, username, password, pk):
    client.login(username=username, password=password)

    instance = QueryJob.objects.get(pk=pk)
    url = reverse(urlnames['detail'], args=[pk])
    response = client.get(url)
    assert response.status_code == status_map['detail'][username], response.json()

    if response.status_code == 200:
        assert response.json().get('table_name') == instance.table_name


@override_settings(QUERY_ANONYMOUS=True)
@pytest.mark.parametrize('query', public_queries)
def test_create_public(db, client, mocker, query):
    mocker.patch(settings.ADAPTER_DATABASE + '.submit_query', mock.Mock())
    mocker.patch(settings.ADAPTER_DATABASE + '.fetch_columns', mock.Mock(return_value=[]))
    mocker.patch(settings.ADAPTER_DATABASE + '.fetch_size', mock.Mock(return_value=100))
    mocker.patch(settings.ADAPTER_DATABASE + '.count_rows', mock.Mock(return_value=100))
    mocker.patch(settings.ADAPTER_DATABASE + '.create_user_schema_if_not_exists', mock.Mock())

    url = reverse(urlnames['list'])
    response = client.post(url, {
        'query_language': 'adql-2.0',
        'query': query
    })
    assert response.status_code == 201, response.json()


@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('query', internal_queries)
def test_create_internal(db, client, mocker, username, password, query):
    mocker.patch(settings.ADAPTER_DATABASE + '.submit_query', mock.Mock())
    mocker.patch(settings.ADAPTER_DATABASE + '.fetch_columns', mock.Mock(return_value=[]))
    mocker.patch(settings.ADAPTER_DATABASE + '.fetch_size', mock.Mock(return_value=100))
    mocker.patch(settings.ADAPTER_DATABASE + '.count_rows', mock.Mock(return_value=100))
    mocker.patch(settings.ADAPTER_DATABASE + '.create_user_schema_if_not_exists', mock.Mock())

    client.login(username=username, password=password)

    url = reverse(urlnames['list'])
    response = client.post(url, {
        'query_language': 'adql-2.0',
        'query': query
    })
    assert response.status_code == status_map['create_internal'][username], response.json()


@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('query', private_queries)
def test_create_private(db, client, mocker, username, password, query):
    mocker.patch(settings.ADAPTER_DATABASE + '.submit_query', mock.Mock())
    mocker.patch(settings.ADAPTER_DATABASE + '.fetch_columns', mock.Mock(return_value=[]))
    mocker.patch(settings.ADAPTER_DATABASE + '.fetch_size', mock.Mock(return_value=100))
    mocker.patch(settings.ADAPTER_DATABASE + '.count_rows', mock.Mock(return_value=100))
    mocker.patch(settings.ADAPTER_DATABASE + '.create_user_schema_if_not_exists', mock.Mock())

    client.login(username=username, password=password)

    url = reverse(urlnames['list'])
    response = client.post(url, {
        'query_language': 'adql-2.0',
        'query': query
    })
    assert response.status_code == status_map['create_private'][username], response.json()


@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('pk', instances)
def test_update(db, client, mocker, username, password, pk):
    mocker.patch(settings.ADAPTER_DATABASE + '.rename_table', mock.Mock())

    client.login(username=username, password=password)

    instance = QueryJob.objects.get(pk=pk)
    instance_table_name = instance.table_name
    url = reverse(urlnames['detail'], args=[pk])
    response = client.put(url, {
        'table_name': 'renamed',
    }, content_type='application/json')
    assert response.status_code == status_map['update'][username], response.json()

    instance.refresh_from_db()
    assert instance.table_name == ('renamed' if response.status_code == 200 else instance_table_name)


@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('pk', instances)
def test_delete(db, client, mocker, username, password, pk):
    mocker.patch(settings.ADAPTER_DATABASE + '.drop_table', mock.Mock())

    client.login(username=username, password=password)

    instance = QueryJob.objects.get(pk=pk)
    instance_phase = instance.phase
    url = reverse(urlnames['detail'], args=[pk])
    response = client.delete(url)
    assert response.status_code == status_map['delete'][username], response.json()

    instance.refresh_from_db()
    if response.status_code == 204:
        assert instance.phase == 'ARCHIVED' if instance_phase == 'COMPLETED' else instance_phase
    else:
        assert instance.phase == instance_phase


@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('pk', instances)
def test_abort(db, client, username, password, pk):
    client.login(username=username, password=password)

    instance = QueryJob.objects.get(pk=pk)
    instance_phase = instance.phase
    url = reverse(urlnames['abort'], args=[pk])
    response = client.put(url)
    assert response.status_code == status_map['update'][username], response.json()

    instance.refresh_from_db()
    if response.status_code == 200:
        assert instance.phase == 'ABORTED' if instance_phase == 'EXECUTING' else instance_phase
    else:
        assert instance.phase == instance_phase


@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('pk', instances)
def test_rows(db, client, username, password, pk):
    client.login(username=username, password=password)

    instance = QueryJob.objects.get(pk=pk)
    url = reverse(urlnames['rows'], args=[pk])
    response = client.get(url)

    if username == 'user':
        if instance.phase == 'COMPLETED':
            assert response.status_code == 200
            assert response.json()['count'] == 10000
        else:
            assert response.status_code == 400
    elif username == 'anonymous':
        assert response.status_code == 403
    else:
        assert response.status_code == 404


@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('pk', instances)
def test_columns(db, client, username, password, pk):
    client.login(username=username, password=password)

    instance = QueryJob.objects.get(pk=pk)
    url = reverse(urlnames['columns'], args=[pk])
    response = client.get(url)

    if username == 'user':
        assert response.status_code == 200
        assert len(response.json()) == (4 if instance.phase == 'COMPLETED' else 0)
    elif username == 'anonymous':
        assert response.status_code == 403
    else:
        assert response.status_code == 404


@pytest.mark.parametrize('format_key', format_keys)
def test_create_download_completed(db, client, format_key):
    client.login(username='user', password='user')

    pk = '1b6c93ef-4161-4402-b1a7-d1237657e807'
    instance = QueryJob.objects.get(pk=pk)
    url = reverse(urlnames['create-download'], args=[pk, 'table'])
    file_name = get_download_file_name(instance, format_key)

    # remove existing file
    Path(settings.QUERY_DOWNLOAD_DIR).joinpath(file_name).unlink(missing_ok=True)

    # file is not existing yet
    response = client.post(url, {
        'format_key': format_key
    })
    assert response.status_code == 200, response.json()

    # file exists
    response = client.post(url, {
        'format_key': format_key
    })
    assert response.status_code == 200, response.json()


@pytest.mark.parametrize('format_key', format_keys)
def test_create_download_executing(db, client, format_key):
    client.login(username='user', password='user')

    pk = '679b5ce8-bbcf-41c2-ba45-2340910bcfae'
    instance = QueryJob.objects.get(pk=pk)
    url = reverse(urlnames['create-download'], args=[pk, 'table'])
    file_name = get_download_file_name(instance, format_key)

    # remove existing file
    Path(settings.QUERY_DOWNLOAD_DIR).joinpath(file_name).unlink(missing_ok=True)

    # file is not existing yet
    response = client.post(url, {
        'format_key': format_key
    })
    assert response.status_code == 400, response.json()


@pytest.mark.parametrize('format_key', format_keys)
def test_stream_completed(db, client, format_key):
    client.login(username='user', password='user')

    pk = '1b6c93ef-4161-4402-b1a7-d1237657e807'
    instance = QueryJob.objects.get(pk=pk)
    url = reverse(urlnames['stream'], args=[pk, format_key])
    file_name = get_download_file_name(instance, format_key)

    # remove existing file
    Path(settings.QUERY_DOWNLOAD_DIR).joinpath(file_name).unlink(missing_ok=True)

    # file is not existing yet
    response = client.get(url)
    assert response.status_code == 200, response.json()


@pytest.mark.parametrize('format_key', format_keys)
def test_stream_executing(db, client, format_key):
    client.login(username='user', password='user')

    pk = '679b5ce8-bbcf-41c2-ba45-2340910bcfae'
    instance = QueryJob.objects.get(pk=pk)
    url = reverse(urlnames['stream'], args=[pk, format_key])
    file_name = get_download_file_name(instance, format_key)

    # remove existing file
    Path(settings.QUERY_DOWNLOAD_DIR).joinpath(file_name).unlink(missing_ok=True)

    # file is not existing yet
    response = client.get(url)
    assert response.status_code == 400, response.json()


def get_download_file_name(instance, format_key):
    file_name = f'{instance.owner.username}/{instance.table_name}'

    if format_key == 'votable':
        return file_name + '.xml'
    elif format_key == 'csv':
        return file_name + '.csv'
    elif format_key == 'fits':
        return file_name + '.fits'
