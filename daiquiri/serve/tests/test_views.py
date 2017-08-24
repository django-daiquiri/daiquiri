from django.test import TestCase

from test_generator.views import TestViewMixin


class ServeViewTestCase(TestCase):

    fixtures = (
        'auth.json',
        'metadata.json'
    )

    users = (
        ('admin', 'admin'),
        ('user', 'user'),
        ('anonymous', None),
    )

class TableTests(TestViewMixin, ServeViewTestCase):

    url_names = {
        'list_view': 'serve_table'
    }

    status_map = {
        'list_view': {
            'admin': 200, 'user': 200, 'anonymous': 200
        }
    }

    def _test_list_viewset(self, username):
        self.assert_list_view(username, {
            'database_name': 'daiquiri_data_obs',
            'table_name': 'stars'
        })
