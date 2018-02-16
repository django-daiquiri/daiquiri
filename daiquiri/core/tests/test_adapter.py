import logging

from django.conf import settings
from django.test import TestCase

from daiquiri.core.adapter import get_adapter

logger = logging.getLogger(__name__)

class CoreAdapterTestCase(TestCase):

    def setUp(self):
        self.adapter = get_adapter()

    def test_fetch_rows_1(self):
        rows = self.adapter.database.fetch_rows('daiquiri_data_obs', 'stars', column_names=None, search=None, filters=None)
        self.assertEqual(len(rows), 10)

    def test_fetch_table(self):
        rows = self.adapter.database.fetch_table('daiquiri_data_obs', 'stars')
        self.assertEqual(rows['type'], 'table')

    def test_fetch_row(self):
        row = self.adapter.database.fetch_row('daiquiri_data_obs', 'stars', column_names=None, search=None, filters={
                'id': '100'
            })
        self.assertEqual(row[1], -12)

    def test_fetch_rows_2(self):
        row = self.adapter.database.fetch_rows('daiquiri_data_obs', 'stars')
        self.assertEqual(row[0], (1, 26, -10.54756, 386.3631))

    def test_fetch_stats(self):
        rows = self.adapter.database.fetch_stats('daiquiri_data_obs', 'stars')
        self.assertEqual(rows[0], 10000)
        self.assertEqual(rows[1], 548864)

    def test_fetch_columns(self):
        columns = self.adapter.database.fetch_columns('daiquiri_archive', 'files')

        self.assertEqual(len(columns), 7)
        self.assertTrue(columns[0]['indexed'])

    def test_fetch_column(self):
        column = self.adapter.database.fetch_column('daiquiri_archive', 'files', 'id')
        self.assertEqual(column['datatype'], 'char', msg=column)

    def test_fetch_column_names(self):
        columns = self.adapter.database.fetch_column_names('daiquiri_data_obs', 'stars')
        self.assertEqual(columns[0], 'id')

    def test_count_rows(self):
        row = self.adapter.database.count_rows('daiquiri_data_obs', 'stars')
        self.assertEqual(row, 10000)

    def test_download_set_table(self):
        database_config = settings.DATABASES['data']

        self.adapter.download.set_table('daiquiri_archive', 'files')

        if database_config['ENGINE'] == 'django.db.backends.mysql':
            # TODO: test
            args_preset = [
                'mysqldump',
                '--compact',
                '--skip-extended-insert',
                '--user=daiquiri_data',
                '--password=daiquiri_data',
                'daiquiri_archive',
                'files'
            ]
        elif database_config['ENGINE'] == 'django.db.backends.postgresql':
            args_preset = [
                'pg_dump',
                '-a',
                '--inserts',
                '--dbname=postgresql://%(USER)s:%(PASSWORD)s@%(HOST)s:%(PORT)s/%(NAME)s' % database_config,
                '--table=daiquiri_archive.files'
            ]

        self.assertEqual(self.adapter.download.args, args_preset)
