import mock

from django.conf import settings
from django.test import TestCase, override_settings

from daiquiri.jobs.tests.mixins import SyncTestMixin
from daiquiri.query.models import QueryJob, Example

@override_settings(QUERY_ANONYMOUS=True)
@mock.patch(settings.ADAPTER_DATABASE + '.submit_query', mock.Mock())
@mock.patch(settings.ADAPTER_DATABASE + '.fetch_nrows', mock.Mock(return_value=100))
@mock.patch(settings.ADAPTER_DATABASE + '.fetch_size', mock.Mock(return_value=100))
@mock.patch(settings.ADAPTER_DATABASE + '.count_rows', mock.Mock(return_value=100))
@mock.patch(settings.ADAPTER_DATABASE + '.rename_table', mock.Mock())
@mock.patch(settings.ADAPTER_DATABASE + '.drop_table', mock.Mock())
class SyncTestCase(SyncTestMixin, TestCase):

    fixtures = (
        'auth.json',
        'metadata.json',
        'jobs.json',
        'queryjobs.json',
        'examples.json'
    )

    users = (
        ('admin', 'admin'),
        ('user', 'user'),
        ('evil', 'evil'),
        ('anonymous', None),
    )

    url_names = {
        'list': 'tap:sync-list'
    }

    jobs = QueryJob.objects.filter(owner__username='user')

    def get_parameter_for_new_jobs(self, username):
        return [{
            'LANG': example.query_language,
            'QUERY': example.query_string
        } for example in Example.objects.filter(access_level='PUBLIC')]

    def get_parameter_for_new_jobs_internal(self, username):
        return [{
            'LANG': example.query_language,
            'QUERY': example.query_string
        } for example in Example.objects.filter(access_level='INTERNAL')]
