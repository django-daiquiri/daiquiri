from django.test import TestCase

from test_generator.views import TestViewMixin, TestListViewMixin


class MetadataViewTestCase(TestViewMixin, TestCase):

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


class ManagementTests(TestListViewMixin, MetadataViewTestCase):

    url_names = {
        'list_view': 'metadata:management'
    }

    status_map = {
        'list_view': {
            'admin': 200, 'manager': 403, 'user': 403, 'anonymous': 302
        }
    }


class PublicSchemaTests(MetadataViewTestCase):

    url_names = {
        'list_view': 'metadata:schema'
    }

    status_map = {
        'list_view': {
            'admin': 200, 'manager': 200, 'user': 200, 'anonymous': 200
        }
    }

    def _test_list_viewset(self, username):
        self.assert_list_view(username, {
            'schema_name': 'daiquiri_data_obs'
        })


class InternalSchemaTests(MetadataViewTestCase):

    url_names = {
        'list_view': 'metadata:schema'
    }

    status_map = {
        'list_view': {
            'admin': 200, 'manager': 200, 'user': 200, 'anonymous': 404
        }
    }

    def _test_list_viewset(self, username):
        self.assert_list_view(username, {
            'schema_name': 'daiquiri_data_sim'
        })


class PrivateSchemaTests(MetadataViewTestCase):

    url_names = {
        'list_view': 'metadata:schema'
    }

    status_map = {
        'list_view': {
            'admin': 404, 'manager': 200, 'user': 404, 'anonymous': 404
        }
    }

    def _test_list_viewset(self, username):
        self.assert_list_view(username, {
            'schema_name': 'daiquiri_archive'
        })


class PublicTableTests(MetadataViewTestCase):

    url_names = {
        'list_view': 'metadata:table'
    }

    status_map = {
        'list_view': {
            'admin': 200, 'manager': 200, 'user': 200, 'anonymous': 200
        }
    }

    def _test_list_viewset(self, username):
        self.assert_list_view(username, {
            'schema_name': 'daiquiri_data_obs',
            'table_name': 'stars'
        })


class InternalTableTests(MetadataViewTestCase):

    url_names = {
        'list_view': 'metadata:table'
    }

    status_map = {
        'list_view': {
            'admin': 200, 'manager': 200, 'user': 200, 'anonymous': 404
        }
    }

    def _test_list_viewset(self, username):
        self.assert_list_view(username, {
            'schema_name': 'daiquiri_data_sim',
            'table_name': 'halos'
        })


class PrivateTableTests(MetadataViewTestCase):

    url_names = {
        'list_view': 'metadata:table'
    }

    status_map = {
        'list_view': {
            'admin': 404, 'manager': 200, 'user': 404, 'anonymous': 404
        }
    }

    def _test_list_viewset(self, username):
        self.assert_list_view(username, {
            'schema_name': 'daiquiri_archive',
            'table_name': 'files'
        })
