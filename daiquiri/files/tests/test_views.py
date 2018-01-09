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


class FileTests(TestViewMixin, FilesViewTestCase):

    url_names = {
        'list_view': 'files:file'
    }

    status_map = {
        'html': {
            'admin': 200, 'manager': 200, 'user': 200, 'anonymous': 404
        },
        'html_a': {
            'admin': 200, 'manager': 200, 'user': 200, 'anonymous': 404
        },
        'html_a_a': {
            'admin': 404, 'manager': 200, 'user': 404, 'anonymous': 404
        },
        'html_a_b': {
            'admin': 404, 'manager': 404, 'user': 404, 'anonymous': 404
        }
    }

    def _test_html(self, username):
        self.assert_view('html', 'get', 'list_view', username, kwargs={
            'file_path': 'html/'
        })

    def _test_html_a(self, username):
        self.assert_view('html_a', 'get', 'list_view', username, kwargs={
            'file_path': 'html/a/'
        })

    def _test_html_a_a(self, username):
        self.assert_view('html_a_a', 'get', 'list_view', username, kwargs={
            'file_path': 'html/a/a/'
        })

    def _test_html_a_b(self, username):
        self.assert_view('html_a_b', 'get', 'list_view', username, kwargs={
            'file_path': 'html/a/b/'
        })
