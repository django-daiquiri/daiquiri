from django.test import TestCase

from test_generator.views import TestListViewMixin


class ArchiveViewTestCase(TestCase):

    fixtures = (
        'auth.json',
    )

    users = (
        ('admin', 'admin'),
        ('user', 'user'),
        ('anonymous', None),
    )


class QueryTests(TestListViewMixin, ArchiveViewTestCase):

    url_names = {
        'list_view': 'archive:archive'
    }

    status_map = {
        'list_view': {
            'admin': 200, 'user': 200, 'anonymous': 302
        }
    }
