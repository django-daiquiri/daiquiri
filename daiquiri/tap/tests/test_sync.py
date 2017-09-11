import mock

from django.test import TestCase

from daiquiri.core.adapter import get_adapter
from daiquiri.jobs.tests.mixins import SyncTestMixin
from daiquiri.query.models import QueryJob, Example

adapter = get_adapter()

mock_execute = mock.Mock()

mock_fetch_stats = mock.Mock()
mock_fetch_stats.return_value = [0, 0]

mock_fetch_pid = mock.Mock()
mock_fetch_pid.return_value = 1

mock_fetch_table = mock.Mock()
mock_fetch_table.return_value = []


@mock.patch.object(adapter.database, 'execute', mock_execute)
@mock.patch.object(adapter.database, 'fetch_stats', mock_fetch_stats)
@mock.patch.object(adapter.database, 'fetch_pid', mock_fetch_pid)
@mock.patch.object(adapter.database, 'fetch_table', mock_fetch_table)
class AsyncTestCase(SyncTestMixin, TestCase):

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
