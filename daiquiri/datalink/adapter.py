from django.conf import settings

from daiquiri.core.adapter import DatabaseAdapter
from daiquiri.core.utils import import_class


def DatalinkAdapter():
    return import_class(settings.DATALINK_ADAPTER)()


class BaseDatalinkAdapter(object):

    tables = settings.DATALINK_TABLES

    def fetch_rows(self):
        adapter = DatabaseAdapter()

        for table in self.tables:
            schema_name, table_name = table.split('.')
            for row in adapter.fetch_rows(schema_name, table_name, page_size=0):
                yield row
