from django.test import TestCase

from test_generator.views import TestListViewMixin


class QueryViewTestCase(TestCase):

    fixtures = (
        'auth.json',
        'metadata.json'
    )

    users = (
        ('admin', 'admin'),
        ('user', 'user'),
        ('anonymous', None),
    )


class QueryTests(TestListViewMixin, QueryViewTestCase):

    url_names = {
        'list_view': 'query:query'
    }

    status_map = {
        'list_view': {
            'admin': 200, 'user': 200, 'anonymous': 302
        }
    }


class ExamplesTests(TestListViewMixin, QueryViewTestCase):

    url_names = {
        'list_view': 'query:examples'
    }

    status_map = {
        'list_view': {
            'admin': 200, 'user': 403, 'anonymous': 302
        }
    }
