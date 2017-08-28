from django.test import TestCase

from test_generator.viewsets import TestViewsetMixin


class ServeTestCase(TestCase):

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

    status_map = {
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


class PublicRowTests(TestViewsetMixin, ServeTestCase):

    url_names = {
        'viewset': 'serve:row'
    }

    status_map = {
        'list_viewset': {
            'admin': 200, 'user': 200, 'anonymous': 200
        }
    }

    def _test_list_viewset(self, username):
        self.assert_list_viewset(username, query_params={
            'database': 'daiquiri_data_obs',
            'table':'stars'
        })


class InternalRowTests(TestViewsetMixin, ServeTestCase):

    url_names = {
        'viewset': 'serve:row'
    }

    status_map = {
        'list_viewset': {
            'admin': 200, 'user': 200, 'anonymous': 404
        }
    }

    def _test_list_viewset(self, username):
        self.assert_list_viewset(username, query_params={
            'database': 'daiquiri_data_sim',
            'table':'particles'
        })


class UserRowTests(TestViewsetMixin, ServeTestCase):

    url_names = {
        'viewset': 'serve:row'
    }

    status_map = {
        'list_viewset': {
            'admin': 404, 'user': 200, 'anonymous': 404
        }
    }

    def _test_list_viewset(self, username):
        self.assert_list_viewset(username, query_params={
            'database': 'daiquiri_user_user',
            'table':'test'
        })


class NotFoundRowTests(TestViewsetMixin, ServeTestCase):

    url_names = {
        'viewset': 'serve:row'
    }

    status_map = {
        'list_viewset': {
            'admin': 404, 'user': 404, 'anonymous': 404
        }
    }

    def _test_non_existing_database_viewset(self, username):
        self.assert_list_viewset(username, query_params={
            'database': 'non_existing',
            'table':'stars'
        })

    def _test_non_existing_table_viewset(self, username):
        self.assert_list_viewset(username, query_params={
            'database': 'daiquiri_data_obs',
            'table':'non_existing'
        })

    def _test_non_existing_user_table_viewset(self, username):
        self.assert_list_viewset(username, query_params={
            'database': 'daiquiri_user_user',
            'table':'non_existing'
        })


class PublicColumnTests(TestViewsetMixin, ServeTestCase):

    url_names = {
        'viewset': 'serve:column'
    }

    status_map = {
        'list_viewset': {
            'admin': 200, 'user': 200, 'anonymous': 200
        }
    }

    def _test_list_viewset(self, username):
        self.assert_list_viewset(username, query_params={
            'database': 'daiquiri_data_obs',
            'table':'stars'
        })


class InternalColumnTests(TestViewsetMixin, ServeTestCase):

    url_names = {
        'viewset': 'serve:column'
    }

    status_map = {
        'list_viewset': {
            'admin': 200, 'user': 200, 'anonymous': 404
        }
    }

    def _test_list_viewset(self, username):
        self.assert_list_viewset(username, query_params={
            'database': 'daiquiri_data_sim',
            'table':'particles'
        })


class UserColumnTests(TestViewsetMixin, ServeTestCase):

    url_names = {
        'viewset': 'serve:column'
    }

    status_map = {
        'list_viewset': {
            'admin': 404, 'user': 200, 'anonymous': 404
        }
    }

    def _test_list_viewset(self, username):
        self.assert_list_viewset(username, query_params={
            'database': 'daiquiri_user_user',
            'table':'test'
        })


class NotFoundColumnTests(TestViewsetMixin, ServeTestCase):

    url_names = {
        'viewset': 'serve:column'
    }

    status_map = {
        'list_viewset': {
            'admin': 404, 'user': 404, 'anonymous': 404
        }
    }

    def _test_non_existing_database_viewset(self, username):
        self.assert_list_viewset(username, query_params={
            'database': 'non_existing',
            'table':'stars'
        })

    def _test_non_existing_table_viewset(self, username):
        self.assert_list_viewset(username, query_params={
            'database': 'daiquiri_data_obs',
            'table':'non_existing'
        })

    def _test_non_existing_user_table_viewset(self, username):
        self.assert_list_viewset(username, query_params={
            'database': 'daiquiri_user_user',
            'table':'non_existing'
        })
