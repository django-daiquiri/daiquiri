from datetime import datetime

from django.apps import apps
from django.conf import settings
from django.utils.timezone import now

from daiquiri.core.adapter import DatabaseAdapter
from daiquiri.core.constants import ACCESS_LEVEL_PUBLIC
from daiquiri.core.utils import get_doi, import_class


def OaiAdapter():
    return import_class(settings.OAI_ADAPTER)()


class BaseOaiAdapter(object):
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
            for method in ['get_%s_list' % resource_type,
                           'get_%s' % resource_type,
                           'get_%s_record' % resource_type]:
                if not hasattr(self, method):
                    message = '\'%s\' is declared as resource_type, but \'%s\' object has no attribute \'%s\'' % (
                        resource_type, self.__class__.__name__, method)
                    raise NotImplementedError(message)

            try:
                for metadata_prefix in self.get_metadata_prefixes(resource_type):
                    self.get_serializer_class(metadata_prefix, resource_type)
            except AttributeError as e:
                raise NotImplementedError('"%s" is declared as resource_type, but %s' % (resource_type, e))

    def get_resource_list(self):
        for resource_type in self.resource_types:
            yield from getattr(self, 'get_%s_list' % resource_type)()

    def get_resource(self, record):
        return getattr(self, 'get_%s' % record.resource_type)(record.resource_id)

    def get_record(self, resource_type, resource):
        return getattr(self, 'get_%s_record' % resource_type)(resource)

    def get_metadata_prefixes(self, resource_type):
        metadata_prefixes_attribute = '%s_metadata_prefixes' % resource_type

        if hasattr(self, metadata_prefixes_attribute):
            return getattr(self, metadata_prefixes_attribute)
        else:
            return getattr(self, 'get_%s' % metadata_prefixes_attribute)()

    def get_serializer_class(self, metadata_prefix, resource_type):
        serializer_class_attribute = '%s_%s_serializer_class' % (metadata_prefix, resource_type)

        if hasattr(self, serializer_class_attribute):
            return getattr(self, serializer_class_attribute)
        else:
            return getattr(self, 'get_%s' % serializer_class_attribute)()

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


class MetadataOaiAdapterMixin(object):

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
        identifier = self.get_identifier('schemas/{}'.format(schema))
        datestamp = schema.updated or schema.published or now().date()
        set_spec = 'schemas'
        public = (schema.metadata_access_level == ACCESS_LEVEL_PUBLIC) \
            and (schema.published is not None)

        return schema.pk, identifier, datestamp, set_spec, public

    def get_table_record(self, table):
        identifier = self.get_identifier('tables/{}'.format(table))
        datestamp = table.updated or table.published or now().date()
        set_spec = 'tables'
        public = (table.metadata_access_level == ACCESS_LEVEL_PUBLIC) \
            and (table.published is not None) \
            and (table.schema.metadata_access_level == ACCESS_LEVEL_PUBLIC) \
            and (table.schema.published is not None)

        return table.pk, identifier, datestamp, set_spec, public


class DatalinkOAIAdapterMixin(object):

    tables = settings.DATALINK_TABLES

    datalink_metadata_prefixes = ('oai_dc', 'oai_datacite', 'datacite')

    def get_oai_dc_datalink_serializer_class(self):
        return import_class('daiquiri.datalink.serializers.DublincoreSerializer')

    def get_oai_datacite_datalink_serializer_class(self):
        return import_class('daiquiri.datalink.serializers.DataciteSerializer')

    def get_datacite_datalink_serializer_class(self):
        return import_class('daiquiri.datalink.serializers.DataciteSerializer')

    def get_datalink_list(self):
        for table in self.tables:
            schema_name, table_name = table.split('.')
            rows = DatabaseAdapter().fetch_rows(schema_name, table_name, column_names=['ID', 'access_url'],
                                                page_size=0, filters={'semantics': '#doi'})

            for ID, access_url in rows:
                yield 'datalink', {'id': str(ID), 'doi': get_doi(access_url)}

    def get_datalink(self, pk):
        rows = []
        for table in self.tables:
            schema_name, table_name = table.split('.')
            rows += DatabaseAdapter().fetch_rows(schema_name, table_name, column_names=[
                'access_url', 'description', 'semantics', 'content_type', 'content_length'
            ], filters={'ID': str(pk)})

        datalink = {
            'formats': [],
            'alternate_identifiers': [],
            'related_identifiers': []
        }
        for access_url, description, semantics, content_type, content_length in rows:
            if semantics == '#doi':
                datalink['doi'] = get_doi(access_url)
                datalink['title'] = description

            elif semantics == '#this':
                datalink['formats'].append(content_type)
                datalink['related_identifiers'].append({
                    'related_identifier': access_url,
                    'related_identifier_type': 'URL',
                    'relation_type': 'IsDescribedBy'
                })

            elif semantics == '#documentation':
                datalink['alternate_identifiers'].append({
                    'alternate_identifier': access_url,
                    'alternate_identifier_type': 'URL'
                })

            elif semantics == '#preview':
                datalink['related_identifiers'].append({
                    'related_identifier': access_url,
                    'related_identifier_type': 'URL',
                    'relation_type': 'IsSupplementedBy'
                })

            elif semantics == '#auxiliary':
                datalink['related_identifiers'].append({
                    'related_identifier': access_url,
                    'related_identifier_type': 'URL',
                    'relation_type': 'References'
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


class RegistryOaiAdapterMixin(object):

    # services to apear in the registry oai records
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
            return getattr(self, 'get_%s_service' % pk)()

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
                        DatalinkOAIAdapterMixin,
                        BaseOaiAdapter):

    resource_types = ['service', 'schema', 'table', 'datalink']
