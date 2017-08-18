from django.core.urlresolvers import reverse

from test_generator.viewsets import TestModelViewsetMixin

from daiquiri.core.tests import TestCase

from .models import Database, Table, Column, Function


class MetadataTestCase(TestCase):

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
        'list_view': {
            'admin': 200, 'user': 403, 'anonymous': 302
        },
        'list_viewset': {
            'admin': 200, 'user': 403, 'anonymous': 403
        },
        'retrieve_viewset': {
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
        'discover_viewset': {
            'admin': 200, 'user': 403, 'anonymous': 403
        },
        'management_viewset': {
            'admin': 200, 'user': 403, 'anonymous': 403
        },
        'user_viewset': {
            'admin': 200, 'user': 200, 'anonymous': 200
        }
    }


class TestDiscoverViewsetMixin(object):

    def _test_discover_viewset(self, username):

        for instance in self.instances:
            url = reverse(self.url_names['viewset'] + '-discover')
            response = self.client.get(url, self.get_retrieve_viewset_query_params(instance))
            self.assertEqual(response.status_code, self.status_map['discover_viewset'][username], msg=(
                ('username', username),
                ('url', url),
                ('status_code', response.status_code),
                ('content', response.content)
            ))


class TestManagementViewsetMixin(object):

    def _test_management_viewset(self, username):

        url = reverse(self.url_names['viewset'] + '-management')
        response = self.client.get(url, self.get_list_viewset_query_params())

        self.assertEqual(response.status_code, self.status_map['management_viewset'][username], msg=(
            ('username', username),
            ('url', url),
            ('status_code', response.status_code),
            ('content', response.content)
        ))


class TestUserViewsetMixin(object):

    def _test_user_viewset(self, username):

        url = reverse(self.url_names['viewset'] + '-user')
        response = self.client.get(url, self.get_list_viewset_query_params())

        self.assertEqual(response.status_code, self.status_map['user_viewset'][username], msg=(
            ('username', username),
            ('url', url),
            ('status_code', response.status_code),
            ('content', response.content)
        ))


class DatabaseTests(TestUserViewsetMixin, TestManagementViewsetMixin, TestModelViewsetMixin, MetadataTestCase):

    instances = Database.objects.all()
    url_names = {
        'viewset': 'metadata:database'
    }

    def prepare_create_data(self, data):
        data['discover'] = True
        return data


class TableTests(TestDiscoverViewsetMixin, TestModelViewsetMixin, MetadataTestCase):

    instances = Table.objects.all()
    url_names = {
        'viewset': 'metadata:table'
    }

    def prepare_create_data(self, data):
        data['discover'] = True
        return data

    def get_retrieve_viewset_query_params(self, instance):
        return {'database': instance.database.name, 'table': instance.name}


class ColumnTests(TestDiscoverViewsetMixin, TestModelViewsetMixin, MetadataTestCase):

    instances = Column.objects.all()
    url_names = {
        'viewset': 'metadata:column'
    }

    def get_retrieve_viewset_query_params(self, instance):
        return {'database': instance.table.database.name, 'table': instance.table.name, 'column': instance.name}


class FunctionTests(TestUserViewsetMixin, TestManagementViewsetMixin, TestModelViewsetMixin, MetadataTestCase):

    instances = Function.objects.all()
    url_names = {
        'viewset': 'metadata:function'
    }
