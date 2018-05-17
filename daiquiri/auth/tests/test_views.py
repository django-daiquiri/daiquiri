from django.test import TestCase

from test_generator.views import TestListViewMixin

from daiquiri.core.utils import setup_group


class AuthViewTestCase(TestCase):

    fixtures = (
        'auth.json',
    )

    users = (
        ('admin', 'admin'),
        ('manager', 'manager'),
        ('user', 'user'),
        ('anonymous', None),
    )

    status_map = {
        'list_view': {
            'admin': 200, 'manager': 200, 'user': 403, 'anonymous': 302
        }
    }

    def setUp(self):
        setup_group('user_manager')


class UsersTests(TestListViewMixin, AuthViewTestCase):

    url_names = {
        'list_view': 'auth:users'
    }
