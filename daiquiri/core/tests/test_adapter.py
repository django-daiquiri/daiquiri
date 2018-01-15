from django.test import TestCase

from daiquiri.core.adapter import get_adapter


class CoreAdapterTestCase(TestCase):

    def setUp(self):
        self.adapter = get_adapter()

    def test_fetch_rows(self):
        rows = self.adapter.database.fetch_rows('daiquiri_data_obs', 'stars', column_names=None, search=None, filters=None)
        self.assertEqual(len(rows), 10)

    def test_fetch_row(self):
        row = self.adapter.database.fetch_row('daiquiri_data_obs', 'stars', column_names=None, search=None, filters={
                'id': '100'
            })
        self.assertEqual(row[0], 100)
