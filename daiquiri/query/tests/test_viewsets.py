import os
import mock

from django.conf import settings
from django.test import TestCase

from test_generator.viewsets import (
    TestModelViewsetMixin,
    TestListViewsetMixin,
    TestViewsetMixin
)

from daiquiri.core.adapter import get_adapter

from ..models import QueryJob, Example

adapter = get_adapter()

mock_execute = mock.Mock()

mock_fetch_stats = mock.Mock()
mock_fetch_stats.return_value = [0, 0]


class QueryViewsetTestCase(TestCase):

    fixtures = (
        'auth.json',
        'metadata.json',
        'jobs.json',
        'queryjobs.json'
    )

    users = (
        ('admin', 'admin'),
        ('user', 'user'),
        ('evil', 'evil'),
        ('anonymous', None),
    )

    status_map = {
        'list_viewset': {
            'admin': 200, 'user': 200, 'evil': 200, 'anonymous': 403
        }
    }


class StatusTests(TestListViewsetMixin, QueryViewsetTestCase):

    url_names = {
        'viewset': 'query:status'
    }


class FormTests(TestListViewsetMixin, QueryViewsetTestCase):

    url_names = {
        'viewset': 'query:form'
    }


class DropdownTests(TestListViewsetMixin, QueryViewsetTestCase):

    url_names = {
        'viewset': 'query:dropdown'
    }


class JobTests(TestViewsetMixin, QueryViewsetTestCase):

    instances = QueryJob.objects.filter(owner__username='user')

    url_names = {
        'viewset': 'query:job'
    }

    status_map = {
        'list_viewset': {
            'admin': 200, 'user': 200, 'evil': 200, 'anonymous': 403
        },
        'detail_viewset': {
            'admin': 404, 'user': 200, 'evil': 404, 'anonymous': 403
        },
        'create_viewset': {
            'admin': 201, 'user': 201, 'evil': 201, 'anonymous': 403
        },
        'update_viewset': {
            'admin': 404, 'user': 200, 'evil': 404, 'anonymous': 403
        },
        'delete_viewset': {
            'admin': 404, 'user': 204, 'evil': 404, 'anonymous': 403
        },
        'abort_viewset': {
            'admin': 404, 'user': 200, 'evil': 404, 'anonymous': 403
        },
        'download_completed_viewset': {
            'admin': 404, 'user': 200, 'evil': 404, 'anonymous': 403
        },
        'download_executing_viewset': {
            'admin': 404, 'user': 400, 'evil': 404, 'anonymous': 403
        },
        'stream_completed_viewset': {
            'admin': 404, 'user': 200, 'evil': 404, 'anonymous': 403
        },
        'stream_executing_viewset': {
            'admin': 404, 'user': 400, 'evil': 404, 'anonymous': 403
        },
    }

    def _test_list_viewset(self, username):
        self.assert_list_viewset(username)

    def _test_detail_viewset(self, username):
        for instance in self.instances:
            self.assert_detail_viewset(username, kwargs={'pk': instance.pk})

    @mock.patch.object(adapter.database, 'execute', mock_execute)
    @mock.patch.object(adapter.database, 'fetch_stats', mock_fetch_stats)
    def _test_create_viewset(self, username):
        for example in Example.objects.all():
            self.assert_create_viewset(username, data={
                'query_language': example.query_language,
                'query': example.query
            })

    @mock.patch.object(adapter.database, 'execute', mock_execute)
    def _test_update_viewset(self, username):
        for instance in self.instances:
            self.assert_update_viewset(username, kwargs={
                'pk': instance.pk
            }, data={
                'table_name': instance.table_name + '_renamed'
            })

    @mock.patch.object(adapter.database, 'execute', mock_execute)
    def _test_delete_viewset(self, username):
        for instance in self.instances:
            self.assert_delete_viewset(username, kwargs={
                'pk': instance.pk
            })

    def _test_abort_viewset(self, username):
        for instance in self.instances:
            self.assert_viewset('abort_viewset', 'put', 'abort', username, kwargs={
                'pk': instance.pk
            })

    def _test_download_completed_viewset(self, username):

        instance = self.instances.filter(phase='COMPLETED').first()
        self.assert_download_viewset('download_completed_viewset', instance, username)

    def _test_download_executing_viewset(self, username):

        instance = self.instances.filter(phase='EXECUTING').first()
        self.assert_download_viewset('download_executing_viewset', instance, username)

    def assert_download_viewset(self, key, instance, username):

        for format_key in ('csv', 'votable', 'votable-binary', 'votable-binary2'):
            file_name = self.get_download_file_name(instance, format_key)

            for method in ['get', 'put']:
                try:
                    os.remove(os.path.join(settings.QUERY_DOWNLOAD_DIR, file_name))
                except OSError:
                    pass

                # file is not existing yet
                self.assert_viewset(key, method, 'download', username, kwargs={
                    'pk': instance.pk,
                    'format_key': format_key
                })

                # file exists
                self.assert_viewset(key, method, 'download', username, kwargs={
                    'pk': instance.pk,
                    'format_key': format_key
                })

    def _test_stream_completed_viewset(self, username):

        instance = self.instances.filter(phase='COMPLETED').first()
        self.assert_stream_viewset('stream_completed_viewset', instance, username)

    def _test_stream_executing_viewset(self, username):

        instance = self.instances.filter(phase='EXECUTING').first()
        self.assert_stream_viewset('stream_executing_viewset', instance, username)

    def assert_stream_viewset(self, key, instance, username):

        for format_key in ('csv', 'votable', 'votable-binary', 'votable-binary2'):
            file_name = self.get_download_file_name(instance, format_key)

            try:
                os.remove(os.path.join(settings.QUERY_DOWNLOAD_DIR, file_name))
            except OSError:
                pass

            # file is not existing yet
            self.assert_viewset(key, 'get', 'stream', username, kwargs={
                'pk': instance.pk,
                'format_key': format_key
            })

            # file exists
            self.assert_viewset(key, 'get', 'stream', username, kwargs={
                'pk': instance.pk,
                'format_key': format_key
            })

    def get_download_file_name(self, instance, format_key):
        file_name =  '%(username)s/%(table_name)s' % {
            'username': instance.owner.username,
            'table_name': instance.table_name
        }

        if format_key == 'csv':
            return file_name + '.csv'
        elif format_key == 'votable':
            return file_name + '.votable.xml'
        elif format_key == 'votable-binary':
            return file_name + '.votable.binary.xml'
        elif format_key == 'votable-binary2':
            return file_name + '.votable.binary2.xml'

class ExampleViewsetTestCase(TestCase):

    fixtures = (
        'auth.json',
        'metadata.json'
    )

    users = (
        ('admin', 'admin'),
        ('user', 'user'),
        ('anonymous', None),
    )

    status_map = {
        'list_viewset': {
            'admin': 200, 'user': 403, 'anonymous': 403
        },
        'detail_viewset': {
            'admin': 200, 'user': 403, 'anonymous': 403
        },
        'create_viewset': {
            'admin': 201, 'user': 403, 'anonymous': 403
        },
        'update_viewset': {
            'admin': 200, 'user': 403, 'anonymous': 403
        },
        'delete_viewset': {
            'admin': 204, 'user': 403, 'anonymous': 403
        },
        'user_viewset': {
            'admin': 200, 'user': 200, 'anonymous': 403
        }
    }


class ExampleTests(TestModelViewsetMixin, ExampleViewsetTestCase):

    instances = Example.objects.all()
    url_names = {
        'viewset': 'query:example'
    }

    def _test_user_viewset(self, username):
        self.assert_viewset('user_viewset', 'get', 'user', username)
