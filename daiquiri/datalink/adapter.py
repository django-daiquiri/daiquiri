from django.conf import settings
from django.core.exceptions import ValidationError
from django.http import Http404
from django.urls import reverse

from daiquiri.core.adapter import DatabaseAdapter
from daiquiri.core.constants import ACCESS_LEVEL_PUBLIC
from daiquiri.core.utils import get_doi_url, import_class

from .constants import DATALINK_RELATION_TYPES
from .models import Datalink


def DatalinkAdapter():
    return import_class(settings.DATALINK_ADAPTER)()


class BaseDatalinkAdapter(object):
    """
    Each datalink adapter needs to configure a set of resource types.
    resource_types are declare as a list(string), i.e.: ['table', 'schema', ...]

    For each resource type, the following methods need to be implemented:

    * get_<resource_type>_list(self): returns a list of all resources for the resource_type

    * get_<resource_type>_identifier(self, resource): returns the identifier for
      a resource into a list (string)

    * get_<resource_type>_links(self, resource): returns a resource into a list
      of rows of the datalink table (list of python dicts)

    See the mixins below for an example.
    """

    resource_types = []

    def __init__(self):
        for resource_type in self.resource_types:
            for method in ['get_%s_list' % resource_type,
                           'get_%s_identifier' % resource_type,
                           'get_%s_links' % resource_type]:
                if not hasattr(self, method):
                    message = '\'%s\' is declared as resource_type, but \'%s\' object has no attribute \'%s\'' % (
                        resource_type, self.__class__.__name__, method)
                    raise NotImplementedError(message)

    def get_list(self):
        for resource_type in self.resource_types:
            yield from getattr(self, 'get_%s_list' % resource_type)()

    def get_identifier(self, resource_type, resource):
        return getattr(self, 'get_%s_identifier' % resource_type)(resource)

    def get_links(self, resource_type, resource):
        return getattr(self, 'get_%s_links' % resource_type)(resource)

    def get_context_data(self, request, **kwargs):
        context = {}

        if 'ID' in kwargs:
            context['datalinks'] = Datalink.objects.filter(ID=kwargs['ID']).order_by('semantics')
            context['ID'] = kwargs['ID']

        return context


class TablesDatalinkAdapterMixin(object):
    '''
    Gather the datalink entries from Release related Datalink tables (declared in settings.DATALINK_TABLES).
    '''

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
               'content_length': row[8]
            }
        ]


class MetadataDatalinkAdapterMixin(object):
    '''
    Gather the documentation (metadata-page) and doi datalink entries from the metadata for each PUBLIC schemas and tables
    '''

    def get_schema_list(self):
        from daiquiri.metadata.models import Schema

        for schema in Schema.objects.iterator():
            yield 'schema', schema

    def get_schema_identifier(self, schema):
        return schema.name

    def get_schema_links(self, schema):
        schema_links = []

        if schema.metadata_access_level == ACCESS_LEVEL_PUBLIC:
            identifier = self.get_schema_identifier(schema)

            path = reverse('metadata:schema', args=[schema.name])
            access_url = settings.SITE_URL.rstrip('/') + path

            schema_links = [{
               'ID': identifier,
               'access_url': access_url,
               'service_def': '',
               'error_message': '',
               'description': 'Documentation for the {} schema'.format(schema),
               'semantics': '#documentation',
               'content_type': 'application/html',
               'content_length': None
            }]

            if schema.doi:
                schema_links.append({
                   'ID': identifier,
                   'access_url': get_doi_url(schema.doi),
                   'service_def': '',
                   'error_message': '',
                   'description': 'Digital object identifier (DOI) for the {} schema'.format(schema),
                   'semantics': '#doi',
                   'content_type': 'application/html',
                   'content_length': None
                })

            if schema.related_identifiers:
                for related_identifier in schema.related_identifiers:
                    access_url = related_identifier.get('related_identifier')
                    if access_url is not None:
                        description = DATALINK_RELATION_TYPES.get(related_identifier.get('relation_type'), '') \
                                                             .format('the {} schema'.format(schema)) \
                                                             .capitalize()
                        schema_links.append({
                           'ID': identifier,
                           'access_url': access_url,
                           'service_def': '',
                           'error_message': '',
                           'description': description,
                           'semantics': '#auxiliary',
                           'content_type': 'application/html',
                           'content_length': None
                        })

        return schema_links

    def get_table_list(self):
        from daiquiri.metadata.models import Table

        for table in Table.objects.iterator():
            yield 'table', table

    def get_table_identifier(self, table):
        return '{}.{}'.format(table.schema.name, table.name)

    def get_table_links(self, table):
        table_links = []

        if table.metadata_access_level == ACCESS_LEVEL_PUBLIC and \
                table.schema.metadata_access_level == ACCESS_LEVEL_PUBLIC:
            identifier = self.get_table_identifier(table)

            path = reverse('metadata:table', args=[table.schema.name, table.name])
            access_url = settings.SITE_URL.rstrip('/') + path

            table_links.append({
               'ID': identifier,
               'access_url': access_url,
               'service_def': '',
               'error_message': '',
               'description': 'Documentation for the {} table'.format(table),
               'semantics': '#documentation',
               'content_type': 'application/html',
               'content_length': None
            })

            if table.doi:
                table_links.append({
                   'ID': identifier,
                   'access_url': get_doi_url(table.doi),
                   'service_def': '',
                   'error_message': '',
                   'description': 'Digital object identifier (DOI) for the {} table'.format(table),
                   'semantics': '#doi',
                   'content_type': 'application/html',
                   'content_length': None
                })

            if table.related_identifiers:
                for related_identifier in table.related_identifiers:
                    access_url = related_identifier.get('related_identifier')
                    if access_url is not None:
                        description = DATALINK_RELATION_TYPES.get(related_identifier.get('relation_type'), '') \
                                                             .format('the {} table'.format(table)) \
                                                             .capitalize()

                        table_links.append({
                           'ID': identifier,
                           'access_url': access_url,
                           'service_def': '',
                           'error_message': '',
                           'description': description,
                           'semantics': '#auxiliary',
                           'content_type': 'application/html',
                           'content_length': None
                        })

        return table_links


class QueryJobDatalinkAdapterMixin(object):
    '''
    Injects the query job into the context data for the daiquiri.datalinks.views.datalink view
    '''

    def get_context_data(self, request, **kwargs):
        from daiquiri.query.models import QueryJob

        context = super().get_context_data(request, **kwargs)

        if 'job' in request.GET:
            try:
                context['query_job'] = QueryJob.objects.filter_by_owner(request.user).get(pk=request.GET['job'])
            except (QueryJob.DoesNotExist, ValidationError):
                pass

        return context


class DefaultDatalinkAdapter(MetadataDatalinkAdapterMixin,
                             TablesDatalinkAdapterMixin,
                             QueryJobDatalinkAdapterMixin,
                             BaseDatalinkAdapter):

    resource_types = ['datalink', 'schema', 'table']
