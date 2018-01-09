from django.test import TestCase

from test_generator.viewsets import TestViewsetMixin


class FilesViewsetTestCase(TestCase):

    fixtures = (
        'auth.json',
        'files.json'
    )

    users = (
        ('admin', 'admin'),
        ('manager', 'manager'),
        ('user', 'user'),
        ('anonymous', None),
    )


class FileTests(TestViewsetMixin, FilesViewsetTestCase):

    url_names = {
        'viewset': 'files:file'
    }

    status_map = {
        'list_viewset': {
            'admin': 200, 'manager': 200, 'user': 200, 'anonymous': 404
        }
    }

    status_map = {
        'html_index': {
            'admin': 200, 'manager': 200, 'user': 200, 'anonymous': 404
        },
        'index': {
            'admin': 404, 'manager': 404, 'user': 404, 'anonymous': 404
        },
        'a_index': {
            'admin': 404, 'manager': 404, 'user': 404, 'anonymous': 404
        },
        'a_a_index': {
            'admin': 404, 'manager': 200, 'user': 404, 'anonymous': 404
        },
    }

    def _test_html_index(self, username):
        self.assert_viewset('html_index', 'get', 'list', username, query_params={
            'search': 'html/index.html'
        })

    def _test_index(self, username):
        self.assert_viewset('index', 'get', 'list', username, query_params={
            'search': 'index.html'
        })

    def _test_a_index(self, username):
        self.assert_viewset('a_index', 'get', 'list', username, query_params={
            'search': 'a/index.html'
        })

    def _test_a_a_index(self, username):
        self.assert_viewset('a_a_index', 'get', 'list', username, query_params={
            'search': 'a/a/index.html'
        })
