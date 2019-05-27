from django.test import TestCase

from test_generator.viewsets import TestViewsetMixin


class ServeTestCase(TestCase):

    databases = ('default', 'data')

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


class PublicRowTests(TestViewsetMixin, ServeTestCase):

    url_names = {
        'viewset': 'serve:row'
    }

    status_map = {
        'list_viewset': {
            'admin': 200, 'user': 200, 'test': 200, 'anonymous': 200
        }
    }

    def _test_list_viewset(self, username):
        self.assert_list_viewset(username, query_params={
            'schema': 'daiquiri_data_obs',
            'table': 'stars'
        })


class InternalRowTests(TestViewsetMixin, ServeTestCase):

    url_names = {
        'viewset': 'serve:row'
    }

    status_map = {
        'list_viewset': {
            'admin': 200, 'user': 200, 'test': 200, 'anonymous': 404
        }
    }

    def _test_list_viewset(self, username):
        self.assert_list_viewset(username, query_params={
            'schema': 'daiquiri_data_sim',
            'table': 'halos'
        })


class PrivateRowTests(TestViewsetMixin, ServeTestCase):

    url_names = {
        'viewset': 'serve:row'
    }

    status_map = {
        'list_viewset': {
            'admin': 404, 'user': 404, 'test': 200, 'anonymous': 404
        }
    }

    def _test_list_viewset(self, username):
        self.assert_list_viewset(username, query_params={
            'schema': 'daiquiri_data_test',
            'table': 'test'
        })


class NotFoundRowTests(TestViewsetMixin, ServeTestCase):

    url_names = {
        'viewset': 'serve:row'
    }

    status_map = {
        'list_viewset': {
            'admin': 404, 'user': 404, 'test': 404, 'anonymous': 404
        }
    }

    def _test_non_existing_schema_viewset(self, username):
        self.assert_list_viewset(username, query_params={
            'schema': 'non_existing',
            'table': 'stars'
        })

    def _test_non_existing_table_viewset(self, username):
        self.assert_list_viewset(username, query_params={
            'schema': 'daiquiri_data_obs',
            'table': 'non_existing'
        })

    def _test_non_existing_user_table_viewset(self, username):
        self.assert_list_viewset(username, query_params={
            'schema': 'daiquiri_user_user',
            'table': 'non_existing'
        })


class PublicColumnTests(TestViewsetMixin, ServeTestCase):

    url_names = {
        'viewset': 'serve:column'
    }

    status_map = {
        'list_viewset': {
            'admin': 200, 'user': 200, 'test': 200, 'anonymous': 200
        }
    }

    def _test_list_viewset(self, username):
        self.assert_list_viewset(username, query_params={
            'schema': 'daiquiri_data_obs',
            'table': 'stars'
        })


class InternalColumnTests(TestViewsetMixin, ServeTestCase):

    url_names = {
        'viewset': 'serve:column'
    }

    status_map = {
        'list_viewset': {
            'admin': 200, 'user': 200, 'test': 200, 'anonymous': 404
        }
    }

    def _test_list_viewset(self, username):
        self.assert_list_viewset(username, query_params={
            'schema': 'daiquiri_data_sim',
            'table': 'halos'
        })


class PrivateColumnTests(TestViewsetMixin, ServeTestCase):

    url_names = {
        'viewset': 'serve:column'
    }

    status_map = {
        'list_viewset': {
            'admin': 404, 'user': 404, 'test': 200, 'anonymous': 404
        }
    }

    def _test_list_viewset(self, username):
        self.assert_list_viewset(username, query_params={
            'schema': 'daiquiri_data_test',
            'table': 'test'
        })


class NotFoundColumnTests(TestViewsetMixin, ServeTestCase):

    url_names = {
        'viewset': 'serve:column'
    }

    status_map = {
        'list_viewset': {
            'admin': 404, 'user': 404, 'test': 404, 'anonymous': 404
        }
    }

    def _test_non_existing_schema_viewset(self, username):
        self.assert_list_viewset(username, query_params={
            'schema': 'non_existing',
            'table': 'stars'
        })

    def _test_non_existing_table_viewset(self, username):
        self.assert_list_viewset(username, query_params={
            'schema': 'daiquiri_data_obs',
            'table': 'non_existing'
        })

    def _test_non_existing_user_table_viewset(self, username):
        self.assert_list_viewset(username, query_params={
            'schema': 'daiquiri_user_user',
            'table': 'non_existing'
        })
