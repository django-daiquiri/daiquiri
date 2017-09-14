from django.test import TestCase

from test_generator.views import TestViewMixin


class FilesViewTestCase(TestCase):

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


class InternalFileTests(TestViewMixin, FilesViewTestCase):

    url_names = {
        'list_view': 'files:file'
    }

    status_map = {
        'list_view': {
            'admin': 200, 'manager': 200, 'user': 200, 'anonymous': 404
        }
    }

    def _test_get(self, username):
        self.assert_list_view(username, kwargs={
            'file_path': 'html/'
        })


class PrivateFileTests(TestViewMixin, FilesViewTestCase):

    url_names = {
        'list_view': 'files:file'
    }

    status_map = {
        'list_view': {
            'admin': 404, 'manager': 200, 'user': 404, 'anonymous': 404
        }
    }

    def _test_get(self, username):
        self.assert_list_view(username, kwargs={
            'file_path': 'image_00.jpg'
        })
