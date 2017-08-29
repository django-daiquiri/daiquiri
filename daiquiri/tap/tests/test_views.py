from django.test import TestCase

from test_generator.views import TestListViewMixin


class TapViewTestCase(TestCase):

    fixtures = (
        'auth.json',
        'metadata.json',
        'examples.json'
    )

    users = (
        ('admin', 'admin'),
        ('user', 'user'),
        ('anonymous', None),
    )


class RootTests(TestListViewMixin, TapViewTestCase):

    url_names = {
        'list_view': 'tap:root'
    }

    status_map = {
        'list_view': {
            'admin': 200, 'user': 200, 'anonymous': 200
        }
    }


class AvailabilityTests(TestListViewMixin, TapViewTestCase):

    url_names = {
        'list_view': 'tap:availability'
    }

    status_map = {
        'list_view': {
            'admin': 200, 'user': 200, 'anonymous': 200
        }
    }


class CapabilitiesTests(TestListViewMixin, TapViewTestCase):

    url_names = {
        'list_view': 'tap:capabilities'
    }

    status_map = {
        'list_view': {
            'admin': 200, 'user': 200, 'anonymous': 200
        }
    }


class TablesTests(TestListViewMixin, TapViewTestCase):

    url_names = {
        'list_view': 'tap:tables'
    }

    status_map = {
        'list_view': {
            'admin': 200, 'user': 200, 'anonymous': 200
        }
    }


class ExamplesTests(TestListViewMixin, TapViewTestCase):

    url_names = {
        'list_view': 'tap:examples'
    }

    status_map = {
        'list_view': {
            'admin': 200, 'user': 200, 'anonymous': 200
        }
    }
