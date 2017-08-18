from django.test import TestCase as DjangoTestCase

from test_generator.views import TestListViewMixin


class TestCase(DjangoTestCase):

    languages = (
        'en',
    )


class CoreTestCase(TestCase):

    fixtures = (
        'auth.json',
    )

    languages = (
        'en',
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


class HomeTests(TestListViewMixin, CoreTestCase):

    url_names = {
        'list_view': 'home'
    }
