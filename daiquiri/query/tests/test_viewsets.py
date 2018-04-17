import os
import mock

from django.conf import settings
from django.contrib.auth.models import User, AnonymousUser
from django.test import TestCase

from test_generator.viewsets import (
    TestModelViewsetMixin,
    TestListViewsetMixin,
    TestViewsetMixin
)

from ..models import QueryJob, Example


class QueryViewsetTestCase(TestCase):

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


@mock.patch(settings.ADAPTER_DATABASE + '.submit_query', mock.Mock())
@mock.patch(settings.ADAPTER_DATABASE + '.fetch_nrows', mock.Mock(return_value=100))
@mock.patch(settings.ADAPTER_DATABASE + '.fetch_size', mock.Mock(return_value=100))
@mock.patch(settings.ADAPTER_DATABASE + '.count_rows', mock.Mock(return_value=100))
@mock.patch(settings.ADAPTER_DATABASE + '.rename_table', mock.Mock())
@mock.patch(settings.ADAPTER_DATABASE + '.drop_table', mock.Mock())
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
        'create_download_completed_viewset': {
            'admin': 404, 'user': 200, 'evil': 404, 'anonymous': 403
        },
        'create_download_executing_viewset': {
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

    def _test_create_viewset(self, username):
        if username == 'anonymous':
            user = AnonymousUser()
        else:
            user = User.objects.get(username=username)

        for example in Example.objects.filter_by_access_level(user):
            self.assert_create_viewset(username, data={
                'query_language': example.query_language,
                'query': example.query_string
            })

    def _test_update_viewset(self, username):
        for instance in self.instances:
            self.assert_update_viewset(username, kwargs={
                'pk': instance.pk
            }, data={
                'table_name': instance.table_name + '_renamed'
            })

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

    def _test_create_download_completed_viewset(self, username):

        instance = self.instances.filter(phase='COMPLETED').first()
        self.assert_create_download_viewset('create_download_completed_viewset', instance, username)

    def _test_create_download_executing_viewset(self, username):

        instance = self.instances.filter(phase='EXECUTING').first()
        self.assert_create_download_viewset('create_download_executing_viewset', instance, username)

    def assert_create_download_viewset(self, key, instance, username):

        for format_key in ('csv', 'votable'):
            file_name = self.get_download_file_name(instance, format_key)

            try:
                os.remove(os.path.join(settings.QUERY_DOWNLOAD_DIR, file_name))
            except OSError:
                pass

            # file is not existing yet
            self.assert_viewset(key, 'post', 'create-download', username, data={
                'format_key': format_key
            }, kwargs={
                'pk': instance.pk
            })

            # file exists
            self.assert_viewset(key, 'post', 'create-download', username, data={
                'format_key': format_key
            }, kwargs={
                'pk': instance.pk
            })

    def _test_stream_completed_viewset(self, username):

        instance = self.instances.filter(phase='COMPLETED').first()
        self.assert_stream_viewset('stream_completed_viewset', instance, username)

    def _test_stream_executing_viewset(self, username):

        instance = self.instances.filter(phase='EXECUTING').first()
        self.assert_stream_viewset('stream_executing_viewset', instance, username)

    def assert_stream_viewset(self, key, instance, username):

        for format_key in ('csv', 'votable'):
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
        file_name = '%(username)s/%(table_name)s' % {
            'username': instance.owner.username,
            'table_name': instance.table_name
        }

        if format_key == 'csv':
            return file_name + '.csv'
        elif format_key == 'votable':
            return file_name + '.xml'

# class UserRowTests(TestViewsetMixin, ServeTestCase):

#     url_names = {
#         'viewset': 'serve:row'
#     }

#     status_map = {
#         'list_viewset': {
#             'admin': 404, 'user': 200, 'anonymous': 404
#         }
#     }

#     def _test_list_viewset(self, username):
#         self.assert_list_viewset(username, query_params={
#             'schema': 'daiquiri_user_user',
#             'table': 'test'
#         })


# class UserColumnTests(TestViewsetMixin, ServeTestCase):

#     url_names = {
#         'viewset': 'serve:column'
#     }

#     status_map = {
#         'list_viewset': {
#             'admin': 404, 'user': 200, 'anonymous': 404
#         }
#     }

#     def _test_list_viewset(self, username):
#         self.assert_list_viewset(username, query_params={
#             'schema': 'daiquiri_user_user',
#             'table': 'test'
#         })


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
