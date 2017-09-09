import os

from django.conf import settings
from django.test import TestCase

from test_generator.views import TestViewMixin


class ServeViewTestCase(TestCase):

    fixtures = (
        'auth.json',
        'metadata.json',
        'jobs.json',
        'queryjobs.json'
    )

    users = (
        ('admin', 'admin'),
        ('manager', 'manager'),
        ('user', 'user'),
        ('anonymous', None),
    )


class PublicTests(TestViewMixin, ServeViewTestCase):

    url_names = {
        'list_view': 'serve:table'
    }

    status_map = {
        'list_view': {
            'admin': 200, 'manager': 200, 'user': 200, 'anonymous': 200
        }
    }

    def _test_list_view(self, username):
        self.assert_list_view(username, {
            'database_name': 'daiquiri_data_obs',
            'table_name': 'stars'
        })


class InternalTests(TestViewMixin, ServeViewTestCase):

    url_names = {
        'list_view': 'serve:table'
    }

    status_map = {
        'list_view': {
            'admin': 200, 'manager': 200, 'user': 200, 'anonymous': 404
        }
    }

    def _test_list_view(self, username):
        self.assert_list_view(username, {
            'database_name': 'daiquiri_data_sim',
            'table_name': 'particles'
        })


class UserTests(TestViewMixin, ServeViewTestCase):

    url_names = {
        'list_view': 'serve:table'
    }

    status_map = {
        'list_view': {
            'admin': 404, 'manager': 404, 'user': 200, 'anonymous': 404
        }
    }

    def _test_list_view(self, username):
        self.assert_list_view(username, {
            'database_name': 'daiquiri_user_user',
            'table_name': 'test'
        })


class NotFoundTests(TestViewMixin, ServeViewTestCase):

    url_names = {
        'list_view': 'serve:table'
    }

    status_map = {
        'list_view': {
            'admin': 404, 'manager': 404, 'user': 404, 'anonymous': 404
        }
    }

    def _test_non_existing_database_view(self, username):
        self.assert_list_view(username, {
            'database_name': 'non_existing',
            'table_name': 'stars'
        })

    def _test_non_existing_table_view(self, username):
        self.assert_list_view(username, {
            'database_name': 'daiquiri_data_obs',
            'table_name': 'non_existing'
        })

    def _test_non_existing_user_table_view(self, username):
        self.assert_list_view(username, {
            'database_name': 'daiquiri_user_user',
            'table_name': 'non_existing'
        })


class FileTests(TestViewMixin, ServeViewTestCase):

    url_names = {
        'list_view': 'serve:file'
    }

    status_map = {
        'list_view': {
            'admin': 200, 'manager': 200, 'user': 200, 'anonymous': 404
        }
    }

    def _test_archive_get(self, username):
        self.assert_list_view(username, kwargs={
            'file_path': 'image_00.jpg'
        })


class ArchiveTests(TestViewMixin, ServeViewTestCase):

    url_names = {
        'list_view': 'serve:archive'
    }

    status_map = {
        'list_view': {
            'admin': 404, 'manager': 200, 'user': 404, 'anonymous': 404
        }
    }

    def setUp(self):
        for username, password in self.users:
            try:
                os.remove(os.path.join(settings.SERVE_DOWNLOAD_DIR, username, 'images_preview.zip'))
            except OSError:
                pass

    def _test_archive_get(self, username):

        self.assert_view('list_view', 'get', 'list_view', username, kwargs={
            'database_name': 'daiquiri_data_obs',
            'table_name': 'images',
            'column_name': 'preview'
        })

        self.assert_view('list_view', 'get', 'list_view', username, kwargs={
            'database_name': 'daiquiri_data_obs',
            'table_name': 'images',
            'column_name': 'preview'
        })

    def _test_archive_put(self, username):

        self.assert_view('list_view', 'put', 'list_view', username, kwargs={
            'database_name': 'daiquiri_data_obs',
            'table_name': 'images',
            'column_name': 'preview'
        })

        self.assert_view('list_view', 'put', 'list_view', username, kwargs={
            'database_name': 'daiquiri_data_obs',
            'table_name': 'images',
            'column_name': 'preview'
        })
