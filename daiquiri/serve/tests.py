from django.core.urlresolvers import reverse

from test_generator.viewsets import TestListViewsetMixin

from daiquiri.core.tests import TestCase


class ServeTestCase(TestCase):

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


class PublicRowTests(TestListViewsetMixin, ServeTestCase):

    status_map = {
        'list_viewset': {
            'admin': 200, 'user': 200, 'anonymous': 200
        }
    }

    url_names = {
        'viewset': 'serve:row'
    }

    def get_list_viewset_query_params(self):
        return {
            'database': 'daiquiri_data_obs',
            'table': 'stars'
        }


class InternalRowTests(TestListViewsetMixin, ServeTestCase):

    status_map = {
        'list_viewset': {
            'admin': 200, 'user': 200, 'anonymous': 404
        }
    }

    url_names = {
        'viewset': 'serve:row'
    }

    def get_list_viewset_query_params(self):
        return {
            'database': 'daiquiri_data_sim',
            'table': 'particles'
        }


class PublicColumnTests(TestListViewsetMixin, ServeTestCase):

    status_map = {
        'list_viewset': {
            'admin': 200, 'user': 200, 'anonymous': 200
        }
    }

    url_names = {
        'viewset': 'serve:column'
    }

    def get_list_viewset_query_params(self):
        return {
            'database': 'daiquiri_data_obs',
            'table': 'stars'
        }


class InternalColumnTests(TestListViewsetMixin, ServeTestCase):

    status_map = {
        'list_viewset': {
            'admin': 200, 'user': 200, 'anonymous': 404
        }
    }

    url_names = {
        'viewset': 'serve:column'
    }

    def get_list_viewset_query_params(self):
        return {
            'database': 'daiquiri_data_sim',
            'table': 'particles'
        }
