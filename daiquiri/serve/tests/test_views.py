from django.test import TestCase

from test_generator.views import TestViewMixin


class ServeViewTestCase(TestCase):

    fixtures = (
        'auth.json',
        'metadata.json',
        'jobs.json',
        'queryjobs.json'
    )

    users = (
        ('admin', 'admin'),
        ('user', 'user'),
        ('anonymous', None),
    )


class PublicTests(TestViewMixin, ServeViewTestCase):

    url_names = {
        'list_view': 'serve:table'
    }

    status_map = {
        'list_view': {
            'admin': 200, 'user': 200, 'anonymous': 200
        }
    }

    def _test_list_view(self, username):
        self.assert_list_view(username, {
            'database_name': 'daiquiri_data_obs',
            'table_name': 'stars'
        })


class InternalTests(TestViewMixin, ServeViewTestCase):

    url_names = {
        'list_view': 'serve:table'
    }

    status_map = {
        'list_view': {
            'admin': 200, 'user': 200, 'anonymous': 404
        }
    }

    def _test_list_view(self, username):
        self.assert_list_view(username, {
            'database_name': 'daiquiri_data_sim',
            'table_name': 'particles'
        })


class UserTests(TestViewMixin, ServeViewTestCase):

    url_names = {
        'list_view': 'serve:table'
    }

    status_map = {
        'list_view': {
            'admin': 404, 'user': 200, 'anonymous': 404
        }
    }

    def _test_list_view(self, username):
        self.assert_list_view(username, {
            'database_name': 'daiquiri_user_user',
            'table_name': 'test'
        })


class NotFoundTests(TestViewMixin, ServeViewTestCase):

    url_names = {
        'list_view': 'serve:table'
    }

    status_map = {
        'list_view': {
            'admin': 404, 'user': 404, 'anonymous': 404
        }
    }

    def _test_non_existing_database_view(self, username):
        self.assert_list_view(username, {
            'database_name': 'non_existing',
            'table_name': 'stars'
        })

    def _test_non_existing_table_view(self, username):
        self.assert_list_view(username, {
            'database_name': 'daiquiri_data_obs',
            'table_name': 'non_existing'
        })

    def _test_non_existing_user_table_view(self, username):
        self.assert_list_view(username, {
            'database_name': 'daiquiri_user_user',
            'table_name': 'non_existing'
        })
