import pytest

from django.test import override_settings
from django.urls import reverse
from django.utils.http import urlencode

users = (
    ('admin', 'admin'),
    ('user', 'user'),
    ('test', 'test'),
    ('evil', 'evil'),
    ('anonymous', None),
)

url_names = {
    'list': 'tap:sync-list'
}

instances = [
    '679b5ce8-bbcf-41c2-ba45-2340910bcfae',
    '5527f2b0-7130-466d-b8d2-dbf6c5f700bf',
    'c87926e4-8e5f-4032-a764-826b6a39c171',
    '1b6c93ef-4161-4402-b1a7-d1237657e807'
]

queries_public = [
    'SELECT ra, dec, parallax, id FROM daiquiri_data_obs.stars'
]

queries_internal = [
    'SELECT x, y, z, vx, vy, vz, id FROM daiquiri_data_sim.halos'
]

queries_private = [
    'SELECT id, "bool", "array", matrix FROM daiquiri_data_test.test'
]

uws_ns = '{http://www.ivoa.net/xml/UWS/v1.0}'


@override_settings(QUERY_ANONYMOUS=True)
@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('query', queries_public)
def test_create_post_public(db, client, username, password, query):
    '''
    GET /{jobs} with an ulrencodes set of KEY=VALUE as query params
    creates a job with these parameters and returns a VOTable.
    '''
    client.login(username=username, password=password)

    url = reverse(url_names['list']) + '?' + urlencode({
        'LANG': 'adql-2.0',
        'QUERY': query
    })
    response = client.get(url)

    assert response.status_code == 200


@override_settings(QUERY_ANONYMOUS=True)
@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('query', queries_internal)
def test_create_post_internal(db, client, username, password, query):
    '''
    GET /{jobs} with an ulrencodes set of KEY=VALUE as query params
    creates a job with these parameters and returns a VOTable.
    '''
    client.login(username=username, password=password)

    url = reverse(url_names['list']) + '?' + urlencode({
        'LANG': 'adql-2.0',
        'QUERY': query
    })
    response = client.get(url)

    if username != 'anonymous':
        assert response.status_code == 200
    else:
        assert response.status_code == 400


@override_settings(QUERY_ANONYMOUS=True)
@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('query', queries_private)
def test_create_post_private(db, client, username, password, query):
    '''
    GET /{jobs} with an ulrencodes set of KEY=VALUE as query params
    creates a job with these parameters and returns a VOTable.
    '''
    client.login(username=username, password=password)

    url = reverse(url_names['list']) + '?' + urlencode({
        'LANG': 'adql-2.0',
        'QUERY': query
    })
    response = client.get(url)

    if username == 'test':
        assert response.status_code == 200
    else:
        assert response.status_code == 400


@override_settings(QUERY_ANONYMOUS=True)
@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('query', queries_public)
def test_post_job_list_create_public(db, client, username, password, query):
    '''
    POST /{jobs} with an application/x-www-form-urlencoded set of KEY=VALUE
    creates a job with these parameters and returns a VOTable.
    '''
    client.login(username=username, password=password)

    url = reverse(url_names['list'])
    response = client.post(url, urlencode({
        'LANG': 'adql-2.0',
        'QUERY': query
    }), content_type='application/x-www-form-urlencoded')

    assert response.status_code == 200


@override_settings(QUERY_ANONYMOUS=True)
@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('query', queries_internal)
def test_post_job_list_create_internal(db, client, username, password, query):
    '''
    POST /{jobs} with an application/x-www-form-urlencoded set of KEY=VALUE
    creates a job with these parameters and returns a VOTable.
    '''
    client.login(username=username, password=password)

    url = reverse(url_names['list'])
    response = client.post(url, urlencode({
        'LANG': 'adql-2.0',
        'QUERY': query
    }), content_type='application/x-www-form-urlencoded')

    if username != 'anonymous':
        assert response.status_code == 200
    else:
        assert response.status_code == 400


@override_settings(QUERY_ANONYMOUS=True)
@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('query', queries_private)
def test_post_job_list_create_private(db, client, username, password, query):
    '''
    POST /{jobs} with an application/x-www-form-urlencoded set of KEY=VALUE
    creates a job with these parameters and returns a VOTable.
    '''
    client.login(username=username, password=password)

    url = reverse(url_names['list'])
    response = client.post(url, urlencode({
        'LANG': 'adql-2.0',
        'QUERY': query
    }), content_type='application/x-www-form-urlencoded')

    if username == 'test':
        assert response.status_code == 200
    else:
        assert response.status_code == 400
