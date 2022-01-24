from django.apps import apps
from django.conf import settings

from daiquiri.core.constants import ACCESS_LEVEL_PUBLIC
from daiquiri.core.utils import import_class


def OaiAdapter():
    return import_class(settings.OAI_ADAPTER)()


class BaseOaiAdapter(object):
    """
    Each OAI adapter needs to configure a set of resource types.

    For each resource type, the following methods need to be implemented:

    * get_<resource_type>_list(self): returns a list of all resources for the resource_type

    * get_<resource_type>(self, resource_id):

    * get_<resource_type>_record(self, resource):

    See the mixins below for an example.
    """

    identifier_schema = 'oai'
    identifier_repository = settings.SITE_IDENTIFIER
    identifier_delimiter = ':'

    resource_types = {}

    def get_resource_list(self):
        for resource_type in self.resource_types:
            yield from getattr(self, 'get_%s_list' % resource_type)()

    def get_resource(self, record):
        return getattr(self, 'get_%s' % record.resource_type)(record.resource_id)

    def get_record(self, resource_type, resource):
        return getattr(self, 'get_%s_record' % resource_type)(resource)

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
            return Schema.objects.get(pk=pk)
        except Schema.DoesNotExist:
            return None

    def get_table(self, pk):
        from daiquiri.metadata.models import Table

        try:
            return Table.objects.get(pk=pk)
        except Table.DoesNotExist:
            return None

    def get_schema_record(self, schema):
        identifier = self.get_identifier('schemas/%i' % schema.pk)
        datestamp = schema.updated or schema.published
        set_spec = 'schema'
        public = (schema.metadata_access_level == ACCESS_LEVEL_PUBLIC) \
            and (schema.published is not None)

        return schema.pk, identifier, datestamp, set_spec, public

    def get_table_record(self, table):
        identifier = self.get_identifier('tables/%i' % table.pk)
        datestamp = table.updated or table.published
        set_spec = 'table'
        public = (table.metadata_access_level == ACCESS_LEVEL_PUBLIC) \
            and (table.published is not None) \
            and (table.schema.metadata_access_level == ACCESS_LEVEL_PUBLIC) \
            and (table.schema.published is not None)

        return table.pk, identifier, datestamp, set_spec, public


class DoiMetadataOaiAdapterMixin(MetadataOaiAdapterMixin):

    def get_schema_record(self, schema):
        identifier = self.get_identifier(schema.doi)
        datestamp = schema.updated or schema.published
        set_spec = 'schema'
        public = (schema.metadata_access_level == ACCESS_LEVEL_PUBLIC) \
            and bool(schema.published) \
            and bool(schema.doi)

        return schema.pk, identifier, datestamp, set_spec, public

    def get_table_record(self, table):
        identifier = self.get_identifier(table.doi)
        datestamp = table.updated or table.published
        set_spec = 'table'
        public = (table.metadata_access_level == ACCESS_LEVEL_PUBLIC) \
            and bool(table.published) \
            and bool(table.doi) \
            and (table.schema.metadata_access_level == ACCESS_LEVEL_PUBLIC) \
            and bool(table.schema.published)

        return table.pk, identifier, datestamp, set_spec, public


class RegistryOaiAdapterMixin(object):

    # services to apear in the registry oai records
    # does not need to be customized, active apps will be discovered automatically
    services = {
        1: 'registry',
        2: 'authority',
        3: 'web',
        4: 'tap',
        5: 'conesearch',
        6: 'datalink'
    }

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
        return getattr(self, 'get_%s_service' % self.services[pk])()

    def get_service_record(self, service):
        index = next(k for k, v in self.services.items() if v == service['service'])
        identifier = service['identifier']
        datestamp = settings.SITE_UPDATED
        set_spec = 'ivo_managed'
        public = True

        return index, identifier, datestamp, set_spec, public

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


class DefaultOaiAdapter(RegistryOaiAdapterMixin, DoiMetadataOaiAdapterMixin, BaseOaiAdapter):

    resource_types = {
        'service': ('oai_dc', 'ivo_vor'),
        'schema': ('oai_dc', 'oai_datacite', 'datacite'),
        'table': ('oai_dc', 'oai_datacite', 'datacite'),
    }
