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


class InternalFileTests(TestViewsetMixin, FilesViewsetTestCase):

    url_names = {
        'viewset': 'files:file'
    }

    status_map = {
        'list_viewset': {
            'admin': 200, 'manager': 200, 'user': 200, 'anonymous': 404
        }
    }

    def _test_list_viewset(self, username):
        self.assert_list_viewset(username, query_params={
            'search': 'index.html',
        })


class PrivateFileTests(TestViewsetMixin, FilesViewsetTestCase):

    url_names = {
        'viewset': 'files:file'
    }

    status_map = {
        'list_viewset': {
            'admin': 404, 'manager': 200, 'user': 404, 'anonymous': 404
        }
    }

    def _test_list_viewset(self, username):
        self.assert_list_viewset(username, query_params={
            'search': 'image_00.jpg',
        })
