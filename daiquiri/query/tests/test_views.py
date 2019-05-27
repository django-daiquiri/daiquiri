from django.test import TestCase

from test_generator.views import TestListViewMixin

from daiquiri.core.utils import setup_group


class QueryViewTestCase(TestCase):

    databases = ('default', 'data')

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

    def setUp(self):
        setup_group('query_manager')


class QueryTests(TestListViewMixin, QueryViewTestCase):

    url_names = {
        'list_view': 'query:query'
    }

    status_map = {
        'list_view': {
            'admin': 200, 'manager': 200, 'user': 200, 'anonymous': 302
        }
    }


class ExamplesTests(TestListViewMixin, QueryViewTestCase):

    url_names = {
        'list_view': 'query:examples'
    }

    status_map = {
        'list_view': {
            'admin': 200, 'manager': 200, 'user': 403, 'anonymous': 302
        }
    }
