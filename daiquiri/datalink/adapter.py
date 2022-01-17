from django.conf import settings

from daiquiri.core.adapter import DatabaseAdapter
from daiquiri.core.utils import import_class


def DatalinkAdapter():
    return import_class(settings.DATALINK_ADAPTER)()


class BaseDatalinkAdapter(object):

    def fetch_rows(self):
        raise NotImplementedError


class TablesDatalinkAdapterMixin(object):

    tables = settings.DATALINK_TABLES

    def fetch_tables_rows(self):
        adapter = DatabaseAdapter()

        for table in self.tables:
            schema_name, table_name = table.split('.')
            for row in adapter.fetch_rows(schema_name, table_name, page_size=0):
                yield {
                   'ID': row[1],
                   'access_url': row[2] or '',
                   'service_def': row[3] or '',
                   'error_message': row[4] or '',
                   'description': row[5] or '',
                   'semantics': row[6],
                   'content_type': row[7] or '',
                   'content_length': row[8] or 0
                }
