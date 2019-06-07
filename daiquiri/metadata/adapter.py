from daiquiri.core.constants import ACCESS_LEVEL_PUBLIC
from daiquiri.oai.adapter import BaseOaiAdapter

from .models import Schema, Table
from .serializers.datacite import SchemaDataciteSerializer, TableDataciteSerializer
from .serializers.dublincore import SchemaDublincoreSerializer, TableDublincoreSerializer


class MetadataOaiAdapter(BaseOaiAdapter):

    def get_record(self, resource):
        if isinstance(resource, Schema):
            return self.get_schema_record(resource)
        elif isinstance(resource, Table):
            return self.get_table_record(resource)
        else:
            raise RuntimeError('Unsupported resource')

    def get_resource(self, record):
        prefix = self.get_identifier_prefix()

        if record.identifier.startswith(prefix):
            resource_type, resource_id = record.identifier[len(prefix):].split('/')

            if resource_type == 'schemas':
                return self.get_schema(resource_id)

            elif resource_type == 'tables':
                return self.get_table(resource_id)

            else:
                raise RuntimeError()
        else:
            raise RuntimeError('Wrong prefix')

    def get_resources(self):
        yield Schema.objects.all()
        yield Table.objects.all()

    def get_serializer_class(self, resource, metadata_prefix):
        if isinstance(resource, Schema):
            if metadata_prefix == 'oai_dc':
                return SchemaDublincoreSerializer
            elif metadata_prefix in ['oai_datacite', 'datacite']:
                return SchemaDataciteSerializer
            else:
                raise RuntimeError('metadata_prefix not supported')

        elif isinstance(resource, Table):
            if metadata_prefix == 'oai_dc':
                return TableDublincoreSerializer
            elif metadata_prefix in ['oai_datacite', 'datacite']:
                return TableDataciteSerializer
            else:
                raise RuntimeError('metadata_prefix not supported')

        elif resource is None:
            raise RuntimeError('resource is None')

        else:
            raise RuntimeError('resource_type \'%s\' not supported')

    def get_schema_record(self, schema):
        identifier = self.get_identifier_prefix() + 'schemas/%i' % schema.pk
        datestamp = schema.updated or schema.published
        public = (schema.metadata_access_level == ACCESS_LEVEL_PUBLIC) \
            and (schema.published is not None)

        return identifier, datestamp, public

    def get_table_record(self, table):
        identifier = self.get_identifier_prefix() + 'tables/%i' % table.pk
        datestamp = table.updated or table.published
        public = (table.metadata_access_level == ACCESS_LEVEL_PUBLIC) \
            and (table.published is not None) \
            and (table.schema.metadata_access_level == ACCESS_LEVEL_PUBLIC) \
            and (table.schema.published is not None)

        return identifier, datestamp, public

    def get_schema(self, schema_id):
        try:
            return Schema.objects.filter(
                metadata_access_level=ACCESS_LEVEL_PUBLIC,
                published__isnull=False).get(pk=schema_id)
        except Schema.DoesNotExist:
            return None

    def get_table(self, table_id):
        try:
            return Table.objects.filter(
                schema__metadata_access_level=ACCESS_LEVEL_PUBLIC,
                schema__published__isnull=False,
                metadata_access_level=ACCESS_LEVEL_PUBLIC,
                published__isnull=False).get(pk=table_id)
        except Table.DoesNotExist:
            return None


class DoiMetadataOaiAdapter(MetadataOaiAdapter):

    def get_schema_record(self, schema):
        identifier = (self.get_identifier_prefix() + schema.doi) if schema.doi else None
        datestamp = schema.updated or schema.published
        public = (schema.metadata_access_level == ACCESS_LEVEL_PUBLIC) \
            and (schema.published is not None) \
            and (schema.doi is not None)

        return identifier, datestamp, public

    def get_table_record(self, table):
        identifier = (self.get_identifier_prefix() + table.doi) if table.doi else None
        datestamp = table.updated or table.published
        public = (table.metadata_access_level == ACCESS_LEVEL_PUBLIC) \
            and (table.published is not None) \
            and (table.doi is not None) \
            and (table.schema.metadata_access_level == ACCESS_LEVEL_PUBLIC) \
            and (table.schema.published is not None)

        return identifier, datestamp, public

    def get_schema(self, schema_id):
        try:
            return Schema.objects.filter(
                metadata_access_level=ACCESS_LEVEL_PUBLIC,
                published__isnull=False,
                doi__isnull=False,
            ).get(pk=schema_id)
        except Schema.DoesNotExist:
            return None

    def get_table(self, table_id):
        try:
            return Table.objects.filter(
                schema__metadata_access_level=ACCESS_LEVEL_PUBLIC,
                schema__published__isnull=False,
                schema__doi__isnull=False,
                metadata_access_level=ACCESS_LEVEL_PUBLIC,
                published__isnull=False,
                doi__isnull=False
            ).get(pk=table_id)
        except Table.DoesNotExist:
            return None
