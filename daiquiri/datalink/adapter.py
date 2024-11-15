from django.conf import settings
from django.core.exceptions import ValidationError
from django.urls import reverse

from daiquiri.core.adapter import DatabaseAdapter
from daiquiri.core.constants import ACCESS_LEVEL_PUBLIC
from daiquiri.core.utils import get_doi_url, import_class

from .constants import DATALINK_FIELDS, DATALINK_RELATION_TYPES
from .models import Datalink


def DatalinkAdapter():
    return import_class(settings.DATALINK_ADAPTER)()


class BaseDatalinkAdapter:
    """
    Each datalink adapter needs to configure a set of resource types.
    resource_types are declare as a list(string), i.e.: ['table', 'schema', ...]

    For each resource type, the following methods need to be implemented:

    * get_<resource_type>_list(self): returns a list of all resources for the resource_type

    * get_<resource_type>_identifier(self, resource): returns the identifier for
      a resource into a list (string)

    * get_<resource_type>_links(self, resource): returns a resource into a list
      of rows of the datalink table (list of python dicts)

    There are two further adapters, which do not declare resources:

    * DynamicDatalinkAdapter: the latter does not declare a resource, but will inject on the fly
      extra datalink entries according to the method: get_dyn_datalink_links()

    * QueryJobDatalinkAdapterMixin: The latter does not declare a resource either, but it injects
      extra context information for the datalink viewer.

    See the mixins below for an example.
    """

    resource_types = []

    def __init__(self):
        for resource_type in self.resource_types:
            for method in [f'get_{resource_type}_list',
                           f'get_{resource_type}_identifier',
                           f'get_{resource_type}_links']:
                if not hasattr(self, method):
                    message = f'\'{resource_type}\' is declared as resource_type, but \'{self.__class__.__name__}\' ' \
                               'object has no attribute \'{method}\''
                    raise NotImplementedError(message)

    def get_list(self):
        '''This is only used by rebuild_datalink_table, so it needs to gather only the tabular datalink entries.
        '''
        for resource_type in self.resource_types:
            yield from getattr(self, f'get_{resource_type}_list')()

    def get_identifier(self, resource_type, resource):
        return getattr(self, f'get_{resource_type}_identifier')(resource)

    def get_links(self, resource_type, resource):
        return getattr(self, f'get_{resource_type}_links')(resource)

    def get_context_data(self, request, **kwargs):
        '''Get the datalink related context data for a given request
        '''
        context = {}

        if 'ID' in kwargs:
            # more precise would be to use a serializer instead of list(QuerySet.values())
            context['datalinks'] = list(Datalink.objects.filter(ID=kwargs['ID']).order_by('semantics').values())
            context['ID'] = kwargs['ID']

        return context

    def get_datalink_rows(self, identifiers, **kwargs):
        '''Get the list of datalink entries for the provided identifiers (incl. table- and dynamic- datalink)
        '''
        # get the datalink entries from Datalink Table and metadata (Table and Schema)
        static_datalink_rows = list(Datalink.objects.filter(ID__in=identifiers).values())

        # get the dynamic datalink entries
        dyn_datalink_rows = self.get_dyn_datalink_links(identifiers)
        datalink_rows = static_datalink_rows + dyn_datalink_rows

        # create a full URI for the custom semantics
        for row in datalink_rows:
            if row['semantics'] in settings.DATALINK_CUSTOM_SEMANTICS:
                row['semantics'] = settings.SITE_URL + reverse('datalink:datalink-semantics') + row['semantics']

        field_names = [field['name'] for field in DATALINK_FIELDS]

        try:
            rows = [[link[key] for key in field_names] for link in datalink_rows]
        except KeyError as e:
            class_name = str(self.__class__)
            raise KeyError(f"The key '{e.args[0]}' is missing in one of the dictionaries returned by " \
                           f"{class_name}.get_dyn_datalink_links(id) or in the Datalink model.") from e
        except Exception as e:
            raise e

        # check for missing IDs and return error message
        for identifier in identifiers:
            if not any(filter(lambda row: row[0] == identifier, rows)):
                rows.append((identifier, None, None, f'NotFoundFault: {identifier}', None, None, None, None))

        return rows


class TablesDatalinkAdapterMixin:
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


class MetadataDatalinkAdapterMixin:
    '''
    Gather the documentation (metadata-page) and doi datalink entries from the metadata
    for each PUBLIC schemas and tables
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
               'description': f'Documentation for the {schema} schema',
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
                   'description': f'{schema.title}',
                   'semantics': '#doi',
                   'content_type': 'application/html',
                   'content_length': None
                })

            if schema.related_identifiers:
                for related_identifier in schema.related_identifiers:
                    access_url = related_identifier.get('related_identifier')
                    if access_url is not None:
                        description = DATALINK_RELATION_TYPES.get(related_identifier.get('relation_type'), '') \
                                                             .format(f'the {schema} schema') \
                                                             .capitalize()
                        if related_identifier.get('related_identifier_type') == "DOI":
                            access_url = get_doi_url(access_url)

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
        return f'{table.schema.name}.{table.name}'

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
               'description': f'Documentation for the {table} table',
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
                   'description': f'{table.title}',
                   'semantics': '#doi',
                   'content_type': 'application/html',
                   'content_length': None
                })

            if table.related_identifiers:
                for related_identifier in table.related_identifiers:
                    access_url = related_identifier.get('related_identifier')
                    if access_url is not None:
                        description = DATALINK_RELATION_TYPES.get(related_identifier.get('relation_type'), '') \
                                                             .format(f'the {table} table') \
                                                             .capitalize()

                        if related_identifier.get('related_identifier_type') == "DOI":
                            access_url = get_doi_url(access_url)

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


class DynamicDatalinkAdapterMixin:
    '''Define the interface to dynamically add datalink entries
    '''

    def get_dyn_datalink_links(self, IDs, **kwargs):
        '''No dynamically generated entries. Can be overwritten.

        this method should return a list of dict with the following keys:
             ID, access_url, service_def, error_message, description, semantics, content_type, content_length
        '''
        return([])

    def get_context_data(self, request, **kwargs):
        '''Inject dynamically generated Datalink entries into the context for the daiquiri.datalinks.views.datalink View
        '''
        context = super().get_context_data(request, **kwargs)

        if 'ID' in kwargs:
            context['datalinks'] = context['datalinks'] + self.get_dyn_datalink_links([kwargs['ID']], **kwargs)

        return context


class QueryJobDatalinkAdapterMixin:
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

class DefaultDatalinkAdapter(DynamicDatalinkAdapterMixin,
                             MetadataDatalinkAdapterMixin,
                             TablesDatalinkAdapterMixin,
                             QueryJobDatalinkAdapterMixin,
                             BaseDatalinkAdapter):

    resource_types = ['datalink', 'schema', 'table']
