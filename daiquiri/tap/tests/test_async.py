import xml.etree.ElementTree as et
from unittest import mock

import pytest

from django.conf import settings
from django.test import override_settings
from django.urls import reverse
from django.utils.http import urlencode

import iso8601

from daiquiri.query.models import QueryJob

users = (
    ('admin', 'admin'),
    ('user', 'user'),
    ('test', 'test'),
    ('evil', 'evil'),
    ('anonymous', None),
)

url_names = {
    'list': 'tap:async-list',
    'detail': 'tap:async-detail',
    'results': 'tap:async-results',
    'result': 'tap:async-result',
    'parameters': 'tap:async-parameters',
    'destruction': 'tap:async-destruction',
    'executionduration': 'tap:async-executionduration',
    'phase': 'tap:async-phase',
    'error': 'tap:async-error',
    'quote': 'tap:async-quote',
    'owner': 'tap:async-owner'
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
def test_get_job_list_xml(db, client, username, password):
    '''
    GET /{jobs} returns the job list as <uws:jobs> xml element. The archived
    jobs are not returned.
    '''
    client.login(username=username, password=password)

    url = reverse(url_names['list'])
    response = client.get(url)
    assert response.status_code == 200, response.content

    if username == 'user':
        root = et.fromstring(response.content)

        assert root.tag == uws_ns + 'jobs'
        assert len(root) == 4
        for node in root:
            assert node.tag == uws_ns + 'jobref'


@override_settings(QUERY_ANONYMOUS=True)
@pytest.mark.parametrize(('username', 'password'), users)
def test_get_job_list_xml_phase(db, client, username, password):
    '''
    GET /{jobs}?PHASE=<phase> returns the filtered joblist as <jobs>
    element.
    '''
    client.login(username=username, password=password)

    url = reverse(url_names['list']) + '?PHASE=PENDING&PHASE=ERROR'
    response = client.get(url)
    assert response.status_code == 200, response.content

    if username == 'user':
        root = et.fromstring(response.content)
        assert len(root) == 2


@override_settings(QUERY_ANONYMOUS=True)
@pytest.mark.parametrize(('username', 'password'), users)
def test_get_job_list_xml_after(db, client, username, password):
    '''
    GET /{jobs}?AFTER=2014-09-10T10:01:02.000 returns jobs with startTimes
    after the given [std:iso8601] time in UTC. The archived jobs are not
    returned.
    '''
    client.login(username=username, password=password)

    url = reverse(url_names['list']) + '?AFTER=2017-01-01T01:00:00Z'
    response = client.get(url)
    assert response.status_code == 200, response.content

    if username == 'user':
        root = et.fromstring(response.content)
        assert len(root) == 2


@override_settings(QUERY_ANONYMOUS=True)
@pytest.mark.parametrize(('username', 'password'), users)
def test_get_job_list_xml_last(db, client, username, password):
    '''
    GET /{jobs}?LAST=100 returns the given number of most recent jobs
    ordered by ascending startTimes. The archived jobs are not returned.
    '''
    client.login(username=username, password=password)

    url = reverse(url_names['list']) + '?LAST=3'
    response = client.get(url)
    assert response.status_code == 200, response.content

    if username == 'user':
        root = et.fromstring(response.content)
        assert len(root) == 3


@override_settings(QUERY_ANONYMOUS=True)
@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('query', queries_public)
def test_post_job_list_create_public(db, client, username, password, query):
    '''
    POST /{jobs} with an application/x-www-form-urlencoded set of KEY=VALUE
    creates a job with these parameters and redirects to /{jobs}/{job-id}
    as 303.
    '''
    client.login(username=username, password=password)

    url = reverse(url_names['list'])
    response = client.post(url, urlencode({
        'LANG': 'adql-2.0',
        'QUERY': query
    }), content_type='application/x-www-form-urlencoded')
    assert response.status_code == 303, response.content

    response = client.get(response.url + '/phase')
    assert response.status_code == 200, response.content
    assert response.content.decode() == 'PENDING'


@override_settings(QUERY_ANONYMOUS=True)
@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('query', queries_internal)
def test_post_job_list_create_internal(db, client, username, password, query):
    '''
    POST /{jobs} with an application/x-www-form-urlencoded set of KEY=VALUE
    creates a job with these parameters and redirects to /{jobs}/{job-id}
    as 303.
    '''
    client.login(username=username, password=password)

    url = reverse(url_names['list'])
    response = client.post(url, urlencode({
        'LANG': 'adql-2.0',
        'QUERY': query
    }), content_type='application/x-www-form-urlencoded')

    if username != 'anonymous':
        assert response.status_code == 303, response.content

        response = client.get(response.url + '/phase')
        assert response.status_code == 200, response.content
        assert response.content.decode() == 'PENDING'
    else:
        assert response.status_code == 400, response.content


@override_settings(QUERY_ANONYMOUS=True)
@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('query', queries_private)
def test_post_job_list_create_private(db, client, username, password, query):
    '''
    POST /{jobs} with an application/x-www-form-urlencoded set of KEY=VALUE
    creates a job with these parameters and redirects to /{jobs}/{job-id}
    as 303.
    '''
    client.login(username=username, password=password)

    url = reverse(url_names['list'])
    response = client.post(url, urlencode({
        'LANG': 'adql-2.0',
        'QUERY': query
    }), content_type='application/x-www-form-urlencoded')

    if username == 'test':
        assert response.status_code == 303, response.content

        response = client.get(response.url + '/phase')
        assert response.status_code == 200, response.content
        assert response.content.decode() == 'PENDING'
    else:
        assert response.status_code == 400, response.content


@override_settings(QUERY_ANONYMOUS=True)
@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('query', queries_public)
def test_post_job_list_create_run(db, client, mocker, username, password, query):
    '''
    POST /{jobs} with an application/x-www-form-urlencoded set of
    KEY=VALUE and additionally PHASE=RUN to an non-existing {job-id} creates
    a job with these parameters and runs it.
    '''
    mocker.patch(settings.ADAPTER_DATABASE + '.submit_query', mock.Mock())
    mocker.patch(settings.ADAPTER_DATABASE + '.fetch_nrows', mock.Mock(return_value=100))
    mocker.patch(settings.ADAPTER_DATABASE + '.fetch_size', mock.Mock(return_value=100))
    mocker.patch(settings.ADAPTER_DATABASE + '.fetch_columns', mock.Mock(return_value=[]))
    mocker.patch(settings.ADAPTER_DATABASE + '.count_rows', mock.Mock(return_value=100))
    mocker.patch(settings.ADAPTER_DATABASE + '.create_user_schema_if_not_exists', mock.Mock())

    client.login(username=username, password=password)

    url = reverse(url_names['list'])
    response = client.post(url, urlencode({
        'LANG': 'adql-2.0',
        'QUERY': query,
        'PHASE': 'RUN'
    }), content_type='application/x-www-form-urlencoded')
    assert response.status_code == 303, response.content

    response = client.get(response.url + '/phase')
    assert response.status_code == 200, response.content
    assert response.content.decode() == 'COMPLETED'


@override_settings(QUERY_ANONYMOUS=True)
@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('pk', instances)
def test_get_job_detail(db, client, username, password, pk):
    '''
    GET /{jobs}/{job-id} returns a job as <uws:job> xml element.
    '''
    client.login(username=username, password=password)

    url = reverse(url_names['detail'], kwargs={'pk': pk})
    response = client.get(url)

    if username == 'user':
        assert response.status_code == 200, response.content

        root = et.fromstring(response.content)
        assert root.tag == uws_ns + 'job'
    else:
        assert response.status_code == 404


@override_settings(QUERY_ANONYMOUS=True)
@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('pk', instances)
def test_get_job_results(db, client, username, password, pk):
    '''
    GET /{jobs}/{job-id}/results returns any results of the job {job-id} as
    <uws:results> xml element.
    '''
    client.login(username=username, password=password)

    url = reverse(url_names['results'], kwargs={'pk': pk})
    response = client.get(url)

    if username == 'user':
        assert response.status_code == 200, response.content

        root = et.fromstring(response.content)
        assert root.tag == uws_ns + 'results'
    else:
        assert response.status_code == 404


@override_settings(QUERY_ANONYMOUS=True)
@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('pk', instances)
def test_get_job_result(db, client, username, password, pk):
    '''
    GET /{jobs}/{job-id}/results/result returns a 303 to the stream url for this job.
    '''
    client.login(username=username, password=password)

    job = QueryJob.objects.get(pk=pk)
    url = reverse(url_names['result'], kwargs={
        'pk': pk,
        'result': 'result'
    })
    response = client.get(url)

    if username == 'user':
        if job.phase == 'COMPLETED':
            assert response.status_code == 200, response.content
        else:
            assert response.status_code == 400
    else:
        assert response.status_code == 404


@override_settings(QUERY_ANONYMOUS=True)
@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('pk', instances)
def test_get_job_parameters(db, client, username, password, pk):
    '''
    GET /{jobs}/{job-id}/parameters returns any parameters for the job
    {job-id} as <uws:parameters> xml element.
    '''
    client.login(username=username, password=password)

    url = reverse(url_names['parameters'], kwargs={'pk': pk})
    response = client.get(url)

    if username == 'user':
        assert response.status_code == 200, response.content

        root = et.fromstring(response.content)
        assert root.tag == uws_ns + 'parameters'
    else:
        assert response.status_code == 404


@override_settings(QUERY_ANONYMOUS=True)
@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('pk', instances)
def test_get_job_error(db, client, username, password, pk):
    '''
    GET /{jobs}/{job-id}/error returns any error message associated with
    {job-id} as text.
    '''
    client.login(username=username, password=password)

    url = reverse(url_names['error'], kwargs={'pk': pk})
    response = client.get(url)

    if username == 'user':
        assert response.status_code == 200, response.content
    else:
        assert response.status_code == 404


@override_settings(QUERY_ANONYMOUS=True)
@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('pk', instances)
def test_get_job_delete(db, client, username, password, pk):
    '''
    DELETE /{jobs}/{job-id} sets the job phase to ARCHIVED and deletes the
    results and redirects to /{jobs}/{job-id} as 303.
    '''
    client.login(username=username, password=password)

    url = reverse(url_names['detail'], kwargs={'pk': pk})
    response = client.delete(url)

    if username == 'user':
        job = QueryJob.objects.get(pk=pk)
        redirect_url = 'http://testserver' + reverse(url_names['detail'], kwargs={'pk': pk})

        assert response.status_code == 303
        assert response.url == redirect_url
        assert job.phase == 'ARCHIVED'
    else:
        assert response.status_code == 404


@override_settings(QUERY_ANONYMOUS=True)
@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('pk', instances)
def test_post_job_delete(db, client, username, password, pk):
    '''
    POST /{jobs}/{job-id} with ACTION=DELETE sets the job phase to ARCHIVED
    and deletes the results and redirects to /{jobs}/{job-id} as 303.
    '''
    client.login(username=username, password=password)

    url = reverse(url_names['detail'], kwargs={'pk': pk})
    response = client.post(url, urlencode({'ACTION': 'DELETE'}), content_type='application/x-www-form-urlencoded')

    if username == 'user':
        job = QueryJob.objects.get(pk=pk)
        redirect_url = 'http://testserver' + reverse(url_names['detail'], kwargs={'pk': job.pk})

        assert response.status_code == 303
        assert response.url == redirect_url
        assert job.phase == 'ARCHIVED'
    else:
        assert response.status_code == 404


@override_settings(QUERY_ANONYMOUS=True)
@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('pk', instances)
def test_post_job_invalid(db, client, username, password, pk):
    '''
    POST /{jobs}/{job-id} with invalid ACTION returns 400.
    '''
    client.login(username=username, password=password)

    url = reverse(url_names['detail'], kwargs={'pk': pk})
    response = client.post(url, urlencode({'ACTION': 'not_valid'}), content_type='application/x-www-form-urlencoded')

    if username == 'user':
        assert response.status_code == 400
    else:
        assert response.status_code == 404


@override_settings(QUERY_ANONYMOUS=True)
@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('pk', instances)
def test_post_job_missing(db, client, username, password, pk):
    '''
    POST /{jobs}/{job-id} without ACTION returns 400.
    '''
    client.login(username=username, password=password)

    url = reverse(url_names['detail'], kwargs={'pk': pk})
    response = client.post(url, content_type='application/x-www-form-urlencoded')

    if username == 'user':
        assert response.status_code == 400
    else:
        assert response.status_code == 404


@override_settings(QUERY_ANONYMOUS=True)
@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('pk', instances)
def test_get_job_destruction(db, client, username, password, pk):
    '''
    GET /{jobs}/{job-id}/destruction returns the destruction instant for
    {job-id} as [std:iso8601].
    '''
    client.login(username=username, password=password)

    url = reverse(url_names['destruction'], kwargs={'pk': pk})
    response = client.get(url)

    if username == 'user':
        assert response.status_code == 200, response.content

        job = QueryJob.objects.get(pk=pk)
        if job.destruction_time:
            destruction_time = iso8601.parse_date(response.content.decode())
            assert destruction_time == job.destruction_time
        else:
            assert response.content.decode() == ''
    else:
        assert response.status_code == 404


@override_settings(QUERY_ANONYMOUS=True)
@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('pk', instances)
def test_post_job_destruction(db, client, username, password, pk):
    '''
    POST /{jobs}/{job-id}/destruction with DESTRUCTION={std:iso8601}
    (application/x-www-form-urlencoded) sets the destruction instant for
    {job-id} and redirects to /{jobs}/{job-id} as 303.
    '''
    client.login(username=username, password=password)

    destruction_time = '2016-01-01T00:00:00'

    url = reverse(url_names['destruction'], kwargs={'pk': pk})
    response = client.post(url, urlencode({'DESTRUCTION': destruction_time}),
                           content_type='application/x-www-form-urlencoded')

    if username == 'user':
        job = QueryJob.objects.get(pk=pk)
        redirect_url = 'http://testserver' + reverse(url_names['detail'], kwargs={'pk': pk})

        assert response.status_code == 303
        assert response.url == redirect_url
        assert job.destruction_time == iso8601.parse_date(destruction_time)
    else:
        assert response.status_code == 404


@override_settings(QUERY_ANONYMOUS=True)
@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('pk', instances)
def test_post_job_destruction_invalid(db, client, username, password, pk):
    '''
    POST /{jobs}/{job-id}/destruction with invalid DESTRUCTION returns 400.
    '''
    client.login(username=username, password=password)

    url = reverse(url_names['destruction'], kwargs={'pk': pk})
    response = client.post(url, urlencode({'DESTRUCTION': 'not_a_date'}),
                           content_type='application/x-www-form-urlencoded')

    if username == 'user':
        assert response.status_code == 400
    else:
        assert response.status_code == 404


@override_settings(QUERY_ANONYMOUS=True)
@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('pk', instances)
def test_post_job_destruction_missing(db, client, username, password, pk):
    '''
    POST /{jobs}/{job-id}/destruction without DESTRUCTION returns 400.
    '''
    client.login(username=username, password=password)

    url = reverse(url_names['destruction'], kwargs={'pk': pk})
    response = client.post(url, content_type='application/x-www-form-urlencoded')

    if username == 'user':
        assert response.status_code == 400
    else:
        assert response.status_code == 404


@override_settings(QUERY_ANONYMOUS=True)
@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('pk', instances)
def test_get_job_executionduration(db, client, username, password, pk):
    '''
    GET /{jobs}/{job-id}/executionduration returns the maximum execution
    duration of {job-id} as integer.
    '''
    client.login(username=username, password=password)

    url = reverse(url_names['executionduration'], kwargs={'pk': pk})
    response = client.get(url)

    if username == 'user':
        job = QueryJob.objects.get(pk=pk)
        assert response.status_code == 200, response.content
        assert int(response.content) == job.execution_duration
    else:
        assert response.status_code == 404


@override_settings(QUERY_ANONYMOUS=True)
@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('pk', instances)
def test_post_job_executionduration(db, client, username, password, pk):
    '''
    POST /{jobs}/{job-id}/executionduration with EXECUTIONDURATION={int}
    sets the maximum execution duration of {job-id} and redirects as to
    /{jobs}/{job-id} 303.
    '''
    execution_duration = 60
    client.login(username=username, password=password)

    url = reverse(url_names['executionduration'], kwargs={'pk': pk})
    response = client.post(url, urlencode({'EXECUTIONDURATION': 60}), content_type='application/x-www-form-urlencoded')

    if username == 'user':
        job = QueryJob.objects.get(pk=pk)
        redirect_url = 'http://testserver' + reverse(url_names['detail'], kwargs={'pk': pk})

        assert response.status_code == 303
        assert response.url == redirect_url
        assert job.execution_duration == execution_duration
    else:
        assert response.status_code == 404


@override_settings(QUERY_ANONYMOUS=True)
@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('pk', instances)
def test_post_job_executionduration_invalid(db, client, username, password, pk):
    '''
    POST /{jobs}/{job-id}/executionduration with invalid EXECUTIONDURATION returns 400.
    '''
    client.login(username=username, password=password)

    url = reverse(url_names['executionduration'], kwargs={'pk': pk})
    response = client.post(url, urlencode({'EXECUTIONDURATION': 'not_an_integer'}),
                           content_type='application/x-www-form-urlencoded')

    if username == 'user':
        assert response.status_code == 400
    else:
        assert response.status_code == 404


@override_settings(QUERY_ANONYMOUS=True)
@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('pk', instances)
def test_post_job_executionduration_missing(db, client, username, password, pk):
    '''
    POST /{jobs}/{job-id}/executionduration without EXECUTIONDURATION returns 400.
    '''
    client.login(username=username, password=password)

    url = reverse(url_names['executionduration'], kwargs={'pk': pk})
    response = client.post(url, content_type='application/x-www-form-urlencoded')

    if username == 'user':
        assert response.status_code == 400
    else:
        assert response.status_code == 404


@override_settings(QUERY_ANONYMOUS=True)
@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('pk', instances)
def test_get_job_phase(db, client, username, password, pk):
    '''
    GET /{jobs}/{job-id}/phase returns the phase of job {job-id} as one of
    the fixed strings.
    '''
    client.login(username=username, password=password)

    url = reverse(url_names['phase'], kwargs={'pk': pk})
    response = client.get(url)

    if username == 'user':
        job = QueryJob.objects.get(pk=pk)
        assert response.status_code == 200, response.content
        assert response.content == job.phase.encode()
    else:
        assert response.status_code == 404


@override_settings(QUERY_ANONYMOUS=True)
@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('pk', instances)
def test_post_job_phase_run(db, client, mocker, username, password, pk):
    '''
    POST /{jobs}/{job-id}/phase with PHASE=RUN runs the job {job-id} and
    redirects as to /{jobs}/{job-id} 303.
    '''
    mocker.patch(settings.ADAPTER_DATABASE + '.submit_query', mock.Mock())
    mocker.patch(settings.ADAPTER_DATABASE + '.fetch_size', mock.Mock(return_value=100))
    mocker.patch(settings.ADAPTER_DATABASE + '.count_rows', mock.Mock(return_value=100))
    mocker.patch(settings.ADAPTER_DATABASE + '.create_user_schema_if_not_exists', mock.Mock())

    client.login(username=username, password=password)

    job = QueryJob.objects.get(pk=pk)
    job_phase = job.phase
    url = reverse(url_names['phase'], kwargs={'pk': pk})
    response = client.post(url, urlencode({'PHASE': 'RUN'}), content_type='application/x-www-form-urlencoded')

    if username == 'user':
        if job_phase in ['PENDING']:
            job.refresh_from_db()
            redirect_url = 'http://testserver' + reverse(url_names['detail'], kwargs={'pk': pk})

            assert response.status_code == 303
            assert response.url == redirect_url
            assert job.phase == 'COMPLETED'
        else:
            assert response.status_code == 400

    else:
        assert response.status_code == 404


@override_settings(QUERY_ANONYMOUS=True)
@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('pk', instances)
def test_post_job_phase_abort(db, client, username, password, pk):
    '''
    POST /{jobs}/{job-id}/phase with PHASE=ABORT aborts the job {job-id} and
    redirects as to /{jobs}/{job-id} 303.
    '''
    client.login(username=username, password=password)

    job = QueryJob.objects.get(pk=pk)
    job_phase = job.phase
    url = reverse(url_names['phase'], kwargs={'pk': pk})
    response = client.post(url, urlencode({'PHASE': 'ABORT'}), content_type='application/x-www-form-urlencoded')

    if username == 'user':
        job.refresh_from_db()
        redirect_url = 'http://testserver' + reverse(url_names['detail'], kwargs={'pk': pk})

        assert response.status_code == 303
        assert response.url == redirect_url

        if job_phase in ['QUEUED', 'EXECUTING']:
            assert job.phase == 'ABORTED'
        else:
            assert job.phase == job_phase
    else:
        assert response.status_code == 404


@override_settings(QUERY_ANONYMOUS=True)
@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('pk', instances)
def test_post_job_phase_invalid(db, client, username, password, pk):
    '''
    POST /{jobs}/{job-id}/phase with invalid PHASE returns 400.
    '''
    client.login(username=username, password=password)

    url = reverse(url_names['phase'], kwargs={'pk': pk})
    response = client.post(url, urlencode({'PHASE': 'invalid'}), content_type='application/x-www-form-urlencoded')

    if username == 'user':
        assert response.status_code == 400
    else:
        assert response.status_code == 404


@override_settings(QUERY_ANONYMOUS=True)
@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('pk', instances)
def test_post_job_phase_missing(db, client, username, password, pk):
    '''
    POST /{jobs}/{job-id}/phase without PHASE returns 400.
    '''
    client.login(username=username, password=password)

    url = reverse(url_names['phase'], kwargs={'pk': pk})
    response = client.post(url, content_type='application/x-www-form-urlencoded')

    if username == 'user':
        assert response.status_code == 400
    else:
        assert response.status_code == 404


@override_settings(QUERY_ANONYMOUS=True)
@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('pk', instances)
def test_post_job_phase_unsupported(db, client, username, password, pk):
    '''
    POST /{jobs}/{job-id}/phase with PHASE=unsupported returns 400.
    '''
    client.login(username=username, password=password)

    url = reverse(url_names['phase'], kwargs={'pk': pk})
    response = client.post(url, urlencode({'PHASE': 'unsupported'}), content_type='application/x-www-form-urlencoded')

    if username == 'user':
        assert response.status_code == 400
    else:
        assert response.status_code == 404


@override_settings(QUERY_ANONYMOUS=True)
@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('pk', instances)
def test_get_job_quote(db, client, username, password, pk):
    '''
    GET /{jobs}/{job-id}/quote returns the quote for {job-id} as [std:iso8601].
    '''
    client.login(username=username, password=password)

    url = reverse(url_names['quote'], kwargs={'pk': pk})
    response = client.get(url)

    if username == 'user':
        assert response.status_code == 200, response.content
        assert response.content.decode() == ''
    else:
        assert response.status_code == 404


@override_settings(QUERY_ANONYMOUS=True)
@pytest.mark.parametrize(('username', 'password'), users)
@pytest.mark.parametrize('pk', instances)
def test_get_job_owner(db, client, username, password, pk):
    '''
    GET /{jobs}/{job-id}/owner returns the owner of the job {job-id} as an
    appropriate identifier.
    '''
    client.login(username=username, password=password)

    url = reverse(url_names['owner'], kwargs={'pk': pk})
    response = client.get(url)

    if username == 'user':
        job = QueryJob.objects.get(pk=pk)
        assert response.status_code == 200, response.content
        assert response.content.decode() == job.owner.username
    else:
        assert response.status_code == 404
