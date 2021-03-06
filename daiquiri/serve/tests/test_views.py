from django.test import TestCase

from test_generator.views import TestViewMixin


class ServeViewTestCase(TestCase):

    databases = ('default', 'data', 'tap', 'oai')

    fixtures = (
        'auth.json',
        'metadata.json',
        'jobs.json',
        'queryjobs.json'
    )

    users = (
        ('admin', 'admin'),
        ('user', 'user'),
        ('test', 'test'),
        ('anonymous', None),
    )


class PublicTableTests(TestViewMixin, ServeViewTestCase):

    url_names = {
        'list_view': 'serve:table'
    }

    status_map = {
        'list_view': {
            'admin': 200, 'user': 200, 'test': 200, 'anonymous': 200
        }
    }

    def _test_list_view(self, username):
        self.assert_list_view(username, {
            'schema_name': 'daiquiri_data_obs',
            'table_name': 'stars'
        })


class InternalTableTests(TestViewMixin, ServeViewTestCase):

    url_names = {
        'list_view': 'serve:table'
    }

    status_map = {
        'list_view': {
            'admin': 200, 'user': 200, 'test': 200, 'anonymous': 404
        }
    }

    def _test_list_view(self, username):
        self.assert_list_view(username, {
            'schema_name': 'daiquiri_data_sim',
            'table_name': 'halos'
        })


class PrivateTableTests(TestViewMixin, ServeViewTestCase):

    url_names = {
        'list_view': 'serve:table'
    }

    status_map = {
        'list_view': {
            'admin': 404, 'user': 404, 'test': 200, 'anonymous': 404
        }
    }

    def _test_list_view(self, username):
        self.assert_list_view(username, {
            'schema_name': 'daiquiri_data_test',
            'table_name': 'test'
        })


class NotFoundTableTests(TestViewMixin, ServeViewTestCase):

    url_names = {
        'list_view': 'serve:table'
    }

    status_map = {
        'list_view': {
            'admin': 404, 'user': 404, 'test': 404, 'anonymous': 404
        }
    }

    def _test_non_existing_schema_view(self, username):
        self.assert_list_view(username, {
            'schema_name': 'non_existing',
            'table_name': 'stars'
        })

    def _test_non_existing_table_view(self, username):
        self.assert_list_view(username, {
            'schema_name': 'daiquiri_data_obs',
            'table_name': 'non_existing'
        })

    def _test_non_existing_user_table_view(self, username):
        self.assert_list_view(username, {
            'schema_name': 'daiquiri_user_user',
            'table_name': 'non_existing'
        })
