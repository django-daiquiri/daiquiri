from django.conf import settings

from daiquiri.core.adapter import DatabaseAdapter
from daiquiri.core.utils import import_class


def DatalinkAdapter():
    return import_class(settings.DATALINK_ADAPTER)()


class BaseDatalinkAdapter(object):
    """
    Each datalink adapter needs to configure a set of resource types.

    For each resource type, the following methods need to be implemented:

    * get_<resource_type>_list(self): returns a list of all resources for the resource_type

    * get_<resource_type>_identifier(self, resource): returns the identifier for
      a resource into a list (string)

    * get_<resource_type>_links(self, resource): returns a resource into a list
      of rows of the datalink table (list of python dicts)

    See TablesDatalinkAdapterMixin below for an example.
    """

    resource_types = []

    def get_list(self):
        for resource_type in self.resource_types:
            yield from getattr(self, 'get_%s_list' % resource_type)()

    def get_identifier(self, resource_type, resource):
        return getattr(self, 'get_%s_identifier' % resource_type)(resource)

    def get_links(self, resource_type, resource):
        return getattr(self, 'get_%s_links' % resource_type)(resource)


class TablesDatalinkAdapterMixin(object):

    tables = settings.DATALINK_TABLES

    def get_datalink_list(self):
        for table in self.tables:
            schema_name, table_name = table.split('.')
            for row in DatabaseAdapter().fetch_rows(schema_name, table_name, page_size=0):
                yield 'datalink', row

    def get_datalink_identifier(self, row):
        return row[1]

    def get_datalink_links(self, row):
        return [
            {
               'ID': self.get_datalink_identifier(row),
               'access_url': row[2] or '',
               'service_def': row[3] or '',
               'error_message': row[4] or '',
               'description': row[5] or '',
               'semantics': row[6],
               'content_type': row[7] or '',
               'content_length': row[8] or 0
            }
        ]
