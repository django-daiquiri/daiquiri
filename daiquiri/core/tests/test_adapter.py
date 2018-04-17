import logging

from django.test import TestCase

from daiquiri.core.adapter import DatabaseAdapter

logger = logging.getLogger(__name__)


class CoreAdapterTestCase(TestCase):

    def test_fetch_table(self):
        rows = DatabaseAdapter().fetch_table('daiquiri_data_obs', 'stars')
        self.assertEqual(rows['type'], 'table')

    def test_fetch_row(self):
        row = DatabaseAdapter().fetch_row('daiquiri_data_obs', 'stars', column_names=None, search=None, filters={
            'id': '4551299946478123136'
        })
        self.assertEqual(row[0], 4551299946478123136)

    def test_fetch_rows(self):
        rows = DatabaseAdapter().fetch_rows('daiquiri_data_obs', 'stars')
        self.assertEqual(len(rows), 10)
        self.assertEqual(len(rows[0]), 4)
        self.assertEqual(rows[0][0], 1714709274237701248)

    def test_fetch_rows_filter(self):
        rows = DatabaseAdapter().fetch_rows('daiquiri_data_sim', 'halos', filters={
            'id': '85000000000'
        })
        self.assertEqual(len(rows), 1)
        self.assertEqual(len(rows[0]), 8)
        self.assertEqual(rows[0][0], 85000000000)

    def test_fetch_nrows(self):
        nrows = DatabaseAdapter().fetch_nrows('daiquiri_data_obs', 'stars')
        self.assertEqual(nrows, 10000)

    def test_fetch_size(self):
        size = DatabaseAdapter().fetch_size('daiquiri_data_obs', 'stars')
        self.assertGreater(size, 250000)

    def test_fetch_columns(self):
        columns = DatabaseAdapter().fetch_columns('daiquiri_archive', 'files')
        self.assertEqual(len(columns), 7)
        self.assertTrue(columns[0]['indexed'])

    def test_fetch_column(self):
        column = DatabaseAdapter().fetch_column('daiquiri_archive', 'files', 'id')
        self.assertTrue(column['datatype'].startswith('char'))

    def test_fetch_column_names(self):
        columns = DatabaseAdapter().fetch_column_names('daiquiri_data_obs', 'stars')
        self.assertEqual(columns[0], 'id')

    def test_count_rows(self):
        row = DatabaseAdapter().count_rows('daiquiri_data_obs', 'stars')
        self.assertEqual(row, 10000)
