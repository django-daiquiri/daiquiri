from collections import OrderedDict

from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase

from test_generator.viewsets import TestViewsetMixin, TestListViewsetMixin

from daiquiri.core.adapter import DatabaseAdapter
from daiquiri.archive.models import Collection, ArchiveJob


class ArchiveTestCase(TestCase):

    fixtures = (
        'auth.json',
        'archive.json',
        'jobs.json'
    )

class RowTests(TestViewsetMixin, ArchiveTestCase):

    users = (
        ('manager', 'manager'),
        ('user', 'user'),
        ('anonymous', None),
    )

    url_names = {
        'viewset': 'archive:row'
    }

    status_map = {
        'list_viewset': {
            'manager': 200, 'user': 200, 'anonymous': 403
        }
    }

    count_map = {
        'manager': 38, 'user': 30, 'anonymous': 20
    }

    def _test_list_viewset(self, username):
        msg = self.assert_list_viewset(username)

        # assert the number of returned rows
        if msg['status_code'] == 200:
            self.assertEqual(self.count_map[username], msg['content']['count'], msg=msg)


class ColumnTests(TestListViewsetMixin, ArchiveTestCase):

    users = (
        ('user', 'user'),
        ('anonymous', None),
    )

    url_names = {
        'viewset': 'archive:column'
    }

    status_map = {
        'list_viewset': {
            'user': 200, 'anonymous': 403
        }
    }


class FileTests(TestViewsetMixin, ArchiveTestCase):

    users = (
        ('manager', 'manager'),
        ('user', 'user'),
        ('anonymous', None),
    )

    url_name = 'archive:file-detail'

    def get_status_code(self, username, collection_id):
        if username == 'anonymous':
            return 403

        try:
            Collection.objects.filter_by_access_level(User.objects.get(username=username)).get(name=collection_id)
            return 200
        except Collection.DoesNotExist:
            return 404

    def _test_detail_viewset(self, username):

        schema_name = settings.ARCHIVE_SCHEMA
        table_name = settings.ARCHIVE_TABLE

        rows = DatabaseAdapter().fetch_rows(schema_name, table_name, ['id', 'collection'], None, None, 0, None, None)

        for row in rows:

            url = reverse(self.url_name, kwargs={'pk': row[0]})
            status_code = self.get_status_code(username, row[1])

            response = self.client.get(url)

            msg = OrderedDict((
                ('username', username),
                ('url', url),
                ('row', row),
                ('status_code', response.status_code)
            ))

            self.assertEqual(response.status_code, status_code, msg=msg)

    def _test_detail_viewset_without_download(self, username):

        schema_name = settings.ARCHIVE_SCHEMA
        table_name = settings.ARCHIVE_TABLE

        rows = DatabaseAdapter().fetch_rows(schema_name, table_name, ['id', 'collection'], None, None, 0, None, None)

        for row in rows:

            url = reverse(self.url_name, kwargs={'pk': row[0]}) + '?download='
            status_code = self.get_status_code(username, row[1])

            response = self.client.get(url)

            msg = OrderedDict((
                ('username', username),
                ('url', url),
                ('row', row),
                ('status_code', response.status_code)
            ))

            self.assertEqual(response.status_code, status_code, msg=msg)


class ArchiveTests(TestViewsetMixin, ArchiveTestCase):

    users = (
        ('admin', 'admin'),
        ('user', 'user'),
        ('evil', 'evil'),
        ('anonymous', None),
    )

    url_names = {
        'viewset': 'archive:archive'
    }

    status_map = {
        'detail_viewset': {
            'admin': 404, 'user': 200, 'evil': 404, 'anonymous': 403
        },
        'create_viewset': {
            'admin': 200, 'user': 200, 'evil': 200, 'anonymous': 403
        }
    }

    def tearDown(self):
        for archive_job in ArchiveJob.objects.all():
            archive_job.delete_file()

    def _test_detail_viewset(self, username):
        for instance in ArchiveJob.objects.filter(owner__username='user'):
            open(instance.file_path, 'w').close()
            self.assert_detail_viewset(username, kwargs={'pk': instance.pk})

    def _test_create_new_viewset(self, username):
        self.assert_create_viewset(username, data={'file_ids': ('95362abc-ad62-4403-b04c-8ea64e642d1d','c5e61e94-767d-4a44-9fea-1f1f36318fbe')})

    def _test_create_existing_viewset(self, username):
        self.assert_create_viewset(username, data={'search': 'image_01'})
