from datetime import datetime

from django.apps import apps
from django.conf import settings
from django.utils.timezone import now

from daiquiri.core.adapter import DatabaseAdapter
from daiquiri.core.constants import ACCESS_LEVEL_PUBLIC
from daiquiri.core.utils import get_doi, import_class
from daiquiri.datalink.adapter import DatalinkAdapter


def OaiAdapter():
    return import_class(settings.OAI_ADAPTER)()


class BaseOaiAdapter:
    """
    Each OAI adapter needs to configure a list of resource_types.

    For each resource_type, the following methods need to be implemented:

    * get_<resource_type>_list(self): returns a list of all resources for this resource_type

    * get_<resource_type>(self, resource_id): returns a resources for a given pk

    * get_<resource_type>_record(self, resource): returns the oai record for a given resource

    In addition the following attributes need to be set:

    * <resource_type>_metadata_prefixes: a list of metadata prefixes for this resource_type

    * <metadata_prefix>_<resource_type>_serializer_class: a serializer class for each
      metadata prefix and resource_type

    Instead of these attributes, getter functions can be implemented,
    e.g. get_<resource_type>_metadata_prefixes(self)

    See the mixins below for an example.
    """

    identifier_schema = 'oai'
    identifier_repository = settings.SITE_IDENTIFIER
    identifier_delimiter = ':'

    resource_types = []

    def __init__(self):
        for resource_type in self.resource_types:
            for method in [f'get_{resource_type}_list',
                           f'get_{resource_type}',
                           f'get_{resource_type}_record']:
                if not hasattr(self, method):
                    message = f'\'{resource_type}\' is declared as resource_type, but \'{self.__class__.__name__}\' ' \
                               'object has no attribute \'{method}\''
                    raise NotImplementedError(message)

            for metadata_prefix in self.get_metadata_prefixes(resource_type):
                self.get_serializer_class(metadata_prefix, resource_type)

    def get_resource_list(self):
        for resource_type in self.resource_types:
            yield from getattr(self, f'get_{resource_type}_list')()

    def get_resource(self, record):
        return getattr(self, f'get_{record.resource_type}')(record.resource_id)

    def get_record(self, resource_type, resource):
        return getattr(self, f'get_{resource_type}_record')(resource)

    def get_metadata_prefixes(self, resource_type):
        metadata_prefixes_attribute = f'{resource_type}_metadata_prefixes'

        if hasattr(self, metadata_prefixes_attribute):
            return getattr(self, metadata_prefixes_attribute)
        else:
            return getattr(self, f'get_{metadata_prefixes_attribute}')()

    def get_serializer_class(self, metadata_prefix, resource_type):
        serializer_class_attribute = f'{metadata_prefix}_{resource_type}_serializer_class'
        serializer_class_attribute_method = f'get_{serializer_class_attribute}'

        if hasattr(self, serializer_class_attribute):
            return getattr(self, serializer_class_attribute)
        elif hasattr(self, serializer_class_attribute_method):
            return getattr(self, serializer_class_attribute_method)()
        else:
            message = f'\'{resource_type}\' is declared as resource_type, but \'{self.__class__.__name__}\' ' \
                       'object has no attribute \'{serializer_class_attribute_method}\''
            raise NotImplementedError(message)

    def get_renderer(self, metadata_prefix):
        renderer_class = next(metadata_format['renderer_class']
                              for metadata_format in settings.OAI_METADATA_FORMATS
                              if metadata_format['prefix'] == metadata_prefix)
        return import_class(renderer_class)()

    def get_identifier(self, identifier):
        if identifier is None:
            return None

        if self.identifier_repository:
            return self.identifier_delimiter.join([self.identifier_schema, self.identifier_repository, identifier])
        else:
            return self.identifier_delimiter.join([self.identifier_schema, identifier])

    def get_sample_identifier(self):
        if self.identifier_repository:
            return self.identifier_delimiter.join([self.identifier_schema, self.identifier_repository, 'example'])
        else:
            return self.identifier_delimiter.join([self.identifier_schema, 'example'])


class MetadataOaiAdapterMixin:

    schema_metadata_prefixes = ('oai_dc', 'oai_datacite', 'datacite')
    table_metadata_prefixes = ('oai_dc', 'oai_datacite', 'datacite')

    def get_oai_dc_schema_serializer_class(self):
        return import_class('daiquiri.metadata.serializers.dublincore.DublincoreSchemaSerializer')

    def get_oai_dc_table_serializer_class(self):
        return import_class('daiquiri.metadata.serializers.dublincore.DublincoreTableSerializer')

    def get_oai_datacite_schema_serializer_class(self):
        return import_class('daiquiri.metadata.serializers.datacite.DataciteSchemaSerializer')

    def get_oai_datacite_table_serializer_class(self):
        return import_class('daiquiri.metadata.serializers.datacite.DataciteTableSerializer')

    def get_datacite_schema_serializer_class(self):
        return import_class('daiquiri.metadata.serializers.datacite.DataciteSchemaSerializer')

    def get_datacite_table_serializer_class(self):
        return import_class('daiquiri.metadata.serializers.datacite.DataciteTableSerializer')

    def get_schema_list(self):
        from daiquiri.metadata.models import Schema

        for schema in Schema.objects.iterator():
            yield 'schema', schema

    def get_table_list(self):
        from daiquiri.metadata.models import Table

        for table in Table.objects.iterator():
            yield 'table', table

    def get_schema(self, pk):
        from daiquiri.metadata.models import Schema

        try:
            schema = Schema.objects.get(pk=pk)
            return self.update_metadata(schema)
        except Schema.DoesNotExist:
            return None

    def get_table(self, pk):
        from daiquiri.metadata.models import Table

        try:
            table = Table.objects.get(pk=pk)
            return self.update_metadata(table)
        except Table.DoesNotExist:
            return None

    def update_metadata(self, instance):
        if hasattr(self, 'get_datalink'):
            for key, values in self.get_datalink(str(instance)).items():
                try:
                    attr = getattr(instance, key)
                    if isinstance(attr, dict):
                        attr.update(values)
                    elif isinstance(attr, list):
                        attr += values
                    else:
                        attr = values
                except AttributeError:
                    attr = values

                # update the instance
                setattr(instance, key, attr)

        return instance

    def get_schema_record(self, schema):
        identifier = self.get_identifier(f'schemas/{schema}')
        datestamp = schema.updated or schema.published or now().date()
        set_spec = 'schemas'
        public = (schema.metadata_access_level == ACCESS_LEVEL_PUBLIC) \
            and (schema.published is not None)

        return schema.pk, identifier, datestamp, set_spec, public

    def get_table_record(self, table):
        identifier = self.get_identifier(f'tables/{table}')
        datestamp = table.updated or table.published or now().date()
        set_spec = 'tables'
        public = (table.metadata_access_level == ACCESS_LEVEL_PUBLIC) \
            and (table.published is not None) \
            and (table.schema.metadata_access_level == ACCESS_LEVEL_PUBLIC) \
            and (table.schema.published is not None)

        return table.pk, identifier, datestamp, set_spec, public


class DatalinkOaiAdapterMixin:

    tables = settings.DATALINK_TABLES

    datalink_metadata_prefixes = ('oai_dc', 'oai_datacite', 'datacite')

    def get_oai_dc_datalink_serializer_class(self):
        return import_class('daiquiri.datalink.serializers.DublincoreSerializer')

    def get_oai_datacite_datalink_serializer_class(self):
        return import_class('daiquiri.datalink.serializers.DataciteSerializer')

    def get_datacite_datalink_serializer_class(self):
        return import_class('daiquiri.datalink.serializers.DataciteSerializer')

    def get_datalink_list(self):
        '''This function is used by rebuild_oai_schema only, it only needs to gather
           the doi objects declared via datalink (no other entries).
        '''
        for table in self.tables:
            schema_name, table_name = table.split('.')
            rows = DatabaseAdapter().fetch_rows(schema_name, table_name, column_names=['ID', 'access_url'],
                                                page_size=0, filters={'semantics': '#doi'})

            for ID, access_url in rows:
                yield 'datalink', {'id': str(ID), 'doi': get_doi(access_url)}

    def get_datalink(self, pk):

        adapter = DatalinkAdapter()
        # get all datalink entries: DatalinkTables, Metadata and Dynamic
        rows = adapter.get_datalink_rows([pk])

        datalink = {
            'formats': [],
            'sizes': [],
            'alternate_identifiers': [
                {
                    'alternate_identifier': pk,
                    'alternate_identifier_type': 'datalink'
                }
            ],
            'related_identifiers': [],
        }
        for _, access_url, _, _, description, semantics, content_type, content_length in rows:
            # doi is a custom datalink semantic which means that it will contain the full URL to the description
            # hence, only the end of the semantics string should be checked for #doi
            if semantics.endswith('#doi'):
                datalink['doi'] = get_doi(access_url)
                datalink['title'] = description

            elif semantics == '#this':
                if content_type not in datalink['formats']:
                    datalink['formats'].append(content_type)
                datalink['sizes'].append(f'{content_length} bytes')
                datalink['related_identifiers'].append({
                    'related_identifier': access_url,
                    'related_identifier_type': 'URL',
                    'relation_type': 'IsDescribedBy'
                })

            elif semantics == '#detached-header':
                if content_type not in datalink['formats']:
                    datalink['formats'].append(content_type)
                datalink['related_identifiers'].append({
                    'related_identifier': access_url,
                    'related_identifier_type': 'URL',
                    'relation_type': 'IsSupplementedBy'
                })

            elif semantics == '#documentation':
                datalink['related_identifiers'].append({
                    'related_identifier': access_url,
                    'related_identifier_type': 'URL',
                    'relation_type': 'IsDocumentedBy'
                })

            elif semantics == '#progenitor':
                datalink['related_identifiers'].append({
                    'related_identifier': access_url,
                    'related_identifier_type': 'URL',
                    'relation_type': 'IsDerivedFrom'
                })

            elif semantics == '#preview':
                datalink['alternate_identifiers'].append({
                    'alternate_identifier': access_url,
                    'alternate_identifier_type': 'DOI Landing Page'
                })

            elif semantics == '#preview-image' or semantics == '#auxiliary':
                datalink['related_identifiers'].append({
                    'related_identifier': access_url,
                    'related_identifier_type': 'URL',
                    'relation_type': 'IsSupplementedBy'
                })

        return datalink

    def get_datalink_record(self, datalink):
        if '/' in datalink['id']:
            # follow the convention <set_spec>/<identifier>
            identifier = self.get_identifier(datalink['id'])
            set_spec = datalink['id'].split('/')[0]
        else:
            identifier = self.get_identifier('datalinks/{}'.format(datalink['id']))
            set_spec = 'datalinks'

        datestamp = datetime.strptime(settings.SITE_CREATED, '%Y-%m-%d').date()
        public = True

        return datalink['id'], identifier, datestamp, set_spec, public


class RegistryOaiAdapterMixin:

    # services to appear in the registry oai records
    # does not need to be customized, active apps will be discovered automatically
    services = [
        'registry',
        'authority',
        'web',
        'tap',
        'conesearch',
        'datalink'
    ]

    service_metadata_prefixes = ['oai_dc', 'ivo_vor']

    def get_oai_dc_service_serializer_class(self):
        return import_class('daiquiri.registry.serializers.DublincoreSerializer')

    def get_ivo_vor_service_serializer_class(self):
        return import_class('daiquiri.registry.serializers.VoresourceSerializer')

    def get_service_list(self):
        for pk in self.services:
            service = self.get_service(pk)
            if service is not None:
                yield 'service', service

    def get_service(self, pk):
        if pk in self.services:
            return getattr(self, f'get_{pk}_service')()

    def get_service_record(self, service):
        identifier = service['identifier']
        datestamp = settings.SITE_UPDATED
        set_spec = 'ivo_managed'
        public = True

        return service['service'], identifier, datestamp, set_spec, public

    def get_registry_service(self):
        if apps.is_installed('daiquiri.registry'):
            from daiquiri.registry.vo import get_resource
            return get_resource()

    def get_authority_service(self):
        if apps.is_installed('daiquiri.registry'):
            from daiquiri.registry.vo import get_authority_resource
            return get_authority_resource()

    def get_web_service(self):
        if apps.is_installed('daiquiri.registry'):
            from daiquiri.registry.vo import get_web_resource
            return get_web_resource()

    def get_tap_service(self):
        if apps.is_installed('daiquiri.tap'):
            from daiquiri.tap.vo import get_resource
            return get_resource()

    def get_conesearch_service(self):
        if apps.is_installed('daiquiri.conesearch'):
            from daiquiri.conesearch.vo import get_resource
            return get_resource()

    def get_datalink_service(self):
        if apps.is_installed('daiquiri.datalink'):
            from daiquiri.datalink.vo import get_resource
            return get_resource()


class DefaultOaiAdapter(RegistryOaiAdapterMixin,
                        MetadataOaiAdapterMixin,
                        DatalinkOaiAdapterMixin,
                        BaseOaiAdapter):

    resource_types = ['service', 'schema', 'table', 'datalink']
