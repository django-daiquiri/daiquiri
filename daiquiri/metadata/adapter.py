
from daiquiri.core.constants import ACCESS_LEVEL_PUBLIC
from daiquiri.oai.adapter import BaseOaiAdapter
from daiquiri.registry.adapter import RegistryOaiAdapterMixin

from .models import Schema, Table
from .serializers.datacite import DataciteSchemaSerializer, DataciteTableSerializer
from .serializers.dublincore import DublincoreSchemaSerializer, DublincoreTableSerializer


class MetadataOaiAdapterMixin(object):

    oai_dc_schema_serializer_class = DublincoreSchemaSerializer
    oai_dc_table_serializer_class = DublincoreTableSerializer

    oai_datacite_schema_serializer_class = DataciteSchemaSerializer
    oai_datacite_table_serializer_class = DataciteTableSerializer

    datacite_schema_serializer_class = DataciteSchemaSerializer
    datacite_table_serializer_class = DataciteTableSerializer

    def get_schema_list(self):
        for schema in Schema.objects.iterator():
            yield 'schema', schema

    def get_table_list(self):
        for table in Table.objects.iterator():
            yield 'table', table

    def get_schema(self, pk):
        try:
            return Schema.objects.get(pk=pk)
        except Schema.DoesNotExist:
            return None

    def get_table(self, pk):
        try:
            return Table.objects.get(pk=pk)
        except Table.DoesNotExist:
            return None

    def get_schema_record(self, schema):
        identifier = self.get_identifier('schemas/%i' % schema.pk)
        datestamp = schema.updated or schema.published
        public = (schema.metadata_access_level == ACCESS_LEVEL_PUBLIC) \
            and (schema.published is not None)

        return schema.pk, identifier, datestamp, public

    def get_table_record(self, table):
        identifier = self.get_identifier('tables/%i' % table.pk)
        datestamp = table.updated or table.published
        public = (table.metadata_access_level == ACCESS_LEVEL_PUBLIC) \
            and (table.published is not None) \
            and (table.schema.metadata_access_level == ACCESS_LEVEL_PUBLIC) \
            and (table.schema.published is not None)

        return table.pk, identifier, datestamp, public


class DoiMetadataOaiAdapterMixin(MetadataOaiAdapterMixin):

    def get_schema_record(self, schema):
        identifier = self.get_identifier(schema.doi)
        datestamp = schema.updated or schema.published
        public = (schema.metadata_access_level == ACCESS_LEVEL_PUBLIC) \
            and (schema.published is not None) \
            and (schema.doi is not None)

        return schema.pk, identifier, datestamp, public

    def get_table_record(self, table):
        identifier = self.get_identifier(table.doi)
        datestamp = table.updated or table.published
        public = (table.metadata_access_level == ACCESS_LEVEL_PUBLIC) \
            and (table.published is not None) \
            and (table.doi is not None) \
            and (table.schema.metadata_access_level == ACCESS_LEVEL_PUBLIC) \
            and (table.schema.published is not None)

        return table.pk, identifier, datestamp, public


class MetadataOaiAdapter(MetadataOaiAdapterMixin, BaseOaiAdapter):

    resource_types = {
        'schema': ('oai_dc', 'oai_datacite', 'datacite'),
        'table': ('oai_dc', 'oai_datacite', 'datacite'),
    }


class DoiMetadataOaiAdapter(DoiMetadataOaiAdapterMixin, BaseOaiAdapter):

    resource_types = {
        'schema': ('oai_dc', 'oai_datacite', 'datacite'),
        'table': ('oai_dc', 'oai_datacite', 'datacite'),
    }


class RegistryMetadataOaiAdapter(RegistryOaiAdapterMixin, MetadataOaiAdapterMixin, BaseOaiAdapter):

    resource_types = {
        'service': ('oai_dc', 'ivo_vor'),
        'schema': ('oai_dc', 'oai_datacite', 'datacite'),
        'table': ('oai_dc', 'oai_datacite', 'datacite'),
    }


class RegistryDoiMetadataOaiAdapter(RegistryOaiAdapterMixin, DoiMetadataOaiAdapterMixin, BaseOaiAdapter):

    resource_types = {
        'service': ('oai_dc', 'ivo_vor'),
        'schema': ('oai_dc', 'oai_datacite', 'datacite'),
        'table': ('oai_dc', 'oai_datacite', 'datacite'),
    }
