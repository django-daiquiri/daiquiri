from django.test import TestCase

from daiquiri.core.adapter import get_adapter


class CoreAdapterTestCase(TestCase):

    def setUp(self):
        self.adapter = get_adapter()


    def test_fetch_rows(self):
        rows = self.adapter.database.fetch_rows('daiquiri_data_obs', 'stars', column_names=None, search=None, filters=None)
        self.assertEqual(len(rows), 10)

    def test_fetch_table(self):
        rows = self.adapter.database.fetch_rows('daiquiri_data_obs', 'stars', column_names=None, search=None, filters=None)
        self.assertEqual(row[1], 'table')


    def test_fetch_row(self):
        row = self.adapter.database.fetch_row('daiquiri_data_obs', 'stars', column_names=None, search=None, filters={
                'id': '100'
            })
        self.assertEqual(row[0], 100)


    def test_fetch_stats(self):
        row = self.adapter.database.fetch_stats('daiquiri_data_obs', 'stars')
        self.assertEqual(row[0], 548864)


    def test_fetch_rows(self):
        row = self.adapter.database.fetch_stats('daiquiri_data_obs', 'stars')
        self.assertEqual(rows[0], 10000)
    

    def test_fetch_columns(self):
        columns = self.adapter.database.fetch_stats('daiquiri_archive', 'files')
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
        self.assertEqual((len(rows), 7) && (row[0]['indexed'], True))

    def test_fetch_column(self):
        columns = self.adapter.database.fetch_stats('daiquiri_archive', 'files', 'id')
        self.assertEqual(row[0]['indexed'], True)

    def test_fetch_column_names(self):
        columns = self.adapter.database.fetch_stats('daiquiri_data_obs', 'stars')
        self.assertEqual(row[0], 'id')

    def test_count_rows(self):
        row = self.adapter.database.count_rows('daiquiri_data_obs', 'stars')
        self.assertEqual(rows[0], 10000)





    
