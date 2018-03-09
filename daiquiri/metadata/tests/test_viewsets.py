from django.test import TestCase

from test_generator.viewsets import TestModelViewsetMixin

from ..models import Schema, Table, Column, Function


class MetadataViewsetTestCase(TestCase):

    fixtures = (
        'auth.json',
        'metadata.json'
    )

    users = (
        ('admin', 'admin'),
        ('manager', 'manager'),
        ('user', 'user'),
        ('anonymous', None),
    )

    status_map = {
        'list_viewset': {
            'admin': 200, 'manager': 403, 'user': 403, 'anonymous': 403
        },
        'detail_viewset': {
            'admin': 200, 'manager': 403, 'user': 403, 'anonymous': 403
        },
        'create_viewset': {
            'admin': 201, 'manager': 403, 'user': 403, 'anonymous': 403
        },
        'update_viewset': {
            'admin': 200, 'manager': 403, 'user': 403, 'anonymous': 403
        },
        'delete_viewset': {
            'admin': 204, 'manager': 403, 'user': 403, 'anonymous': 403
        },
        'discover_viewset': {
            'admin': 200, 'manager': 403, 'user': 403, 'anonymous': 403
        },
        'management_viewset': {
            'admin': 200, 'manager': 403, 'user': 403, 'anonymous': 403
        },
        'user_viewset': {
            'admin': 200, 'manager': 200, 'user': 200, 'anonymous': 200
        }
    }


class SchemaTests(TestModelViewsetMixin, MetadataViewsetTestCase):

    instances = Schema.objects.all()
    url_names = {
        'viewset': 'metadata:schema'
    }

    def _test_create_viewset(self, username):
        for instance in self.instances:
            data = self.get_instance_as_dict(instance)
            data['discover'] = True
            self.assert_create_viewset(username, data=data)

    def _test_management_viewset(self, username):
        self.assert_viewset('management_viewset', 'get', 'management', username)

    def _test_user_viewset(self, username):
        self.assert_viewset('user_viewset', 'get', 'user', username)


class TableTests(TestModelViewsetMixin, MetadataViewsetTestCase):

    instances = Table.objects.all()
    url_names = {
        'viewset': 'metadata:table'
    }

    def _test_create_viewset(self, username):
        for instance in self.instances:
            data = self.get_instance_as_dict(instance)
            data['discover'] = True
            self.assert_create_viewset(username, data=data)

    def _test_discover_viewset(self, username):
        for instance in self.instances:
            self.assert_viewset('discover_viewset', 'get', 'discover', username, query_params={
                'schema': instance.schema.name,
                'table': instance.name
            })


class ColumnTests(TestModelViewsetMixin, MetadataViewsetTestCase):

    instances = Column.objects.all()
    url_names = {
        'viewset': 'metadata:column'
    }

    def _test_discover_viewset(self, username):
        for instance in self.instances:
            self.assert_viewset('discover_viewset', 'get', 'discover', username, query_params={
                'schema': instance.table.schema.name,
                'table': instance.table.name,
                'column': instance.name
            })


class FunctionTests(TestModelViewsetMixin, MetadataViewsetTestCase):

    instances = Function.objects.all()
    url_names = {
        'viewset': 'metadata:function'
    }

    def _test_management_viewset(self, username):
        self.assert_viewset('management_viewset', 'get', 'management', username)

    def _test_user_viewset(self, username):
        self.assert_viewset('user_viewset', 'get', 'user', username)
