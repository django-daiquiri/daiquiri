from django.test import TestCase

from test_generator.views import TestListViewMixin


class CoreViewTestCase(TestCase):

    fixtures = (
        'auth.json',
    )

    users = (
        ('admin', 'admin'),
        ('user', 'user'),
        ('anonymous', None),
    )

    status_map = {
        'list_view': {
            'admin': 200, 'user': 200, 'anonymous': 200
        }
    }


class HomeTests(TestListViewMixin, CoreViewTestCase):

    url_names = {
        'list_view': 'home'
    }
