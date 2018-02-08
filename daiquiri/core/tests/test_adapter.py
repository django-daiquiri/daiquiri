import logging
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
        logger.debug('test_fetch_table: %s' % (rows, ))
        self.assertEqual(rows['type'], 'table')

    def test_fetch_row(self):
        row = self.adapter.database.fetch_row('daiquiri_data_obs', 'stars', column_names=None, search=None, filters={
                'id': '100'
            })
        logger.debug('test_fetch_row: %s' % (str(row)))
        self.assertEqual(row[1], -12)

    def test_fetch_rows_2(self):
        row = self.adapter.database.fetch_rows('daiquiri_data_obs', 'stars')
        logger.debug('test_fetch_rows_2: %s' % (row, ))
        self.assertEqual(row[0], (1, 26, -10.54756, 386.3631))

    def test_fetch_stats(self):
        rows = self.adapter.database.fetch_stats('daiquiri_data_obs', 'stars')
        logger.debug('test_fetch_stats: %s' % (rows, ))
        self.assertEqual(rows[0], 10000)
        self.assertEqual(rows[1], 548864)

    def test_fetch_columns(self):
        columns = self.adapter.database.fetch_columns('daiquiri_archive', 'files')
        #  column_name |          data_type
        #  -------------+-----------------------------
        #  id          | character
        #  timestamp   | timestamp without time zone
        #  file        | character varying
        #  collection  | character
        #  path        | text
        #  ra          | real
        #  de          | real
        # id is indexed
        logger.debug('test_fetch_columns columns: %s' % (columns, ))
        if len(columns) == 7 and columns[0]['indexed'] == False:
            test = True
        self.assertEqual(test, True)

    def test_fetch_column(self):
        column = self.adapter.database.fetch_column('daiquiri_archive', 'files', 'id')
        logger.debug('test_fetch_column: %s' % (column, ))
        self.assertEqual(column['datatype'], 'character')

    def test_fetch_column_names(self):
        columns = self.adapter.database.fetch_column_names('daiquiri_data_obs', 'stars')
        logger.debug('test_fetch_column_names: %s' % (columns, ))
        self.assertEqual(columns[0], 'id')

    def test_count_rows(self):
        row = self.adapter.database.count_rows('daiquiri_data_obs', 'stars')
        logger.debug('test_count_rows: %s' % (row, ))
        self.assertEqual(row, 10000)






