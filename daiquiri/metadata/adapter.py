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
        resource_identifier = self.strip_identifier_prefix(record.identifier)
        resource_type, resource_id = resource_identifier.split('/')

        if resource_type == 'schemas':
            try:
                return Schema.objects.filter(
                    metadata_access_level=ACCESS_LEVEL_PUBLIC,
                    published__isnull=False).get(pk=resource_id)
            except Schema.DoesNotExist:
                return None

        elif resource_type == 'tables':
            try:
                return Table.objects.filter(
                    schema__metadata_access_level=ACCESS_LEVEL_PUBLIC,
                    schema__published__isnull=False,
                    metadata_access_level=ACCESS_LEVEL_PUBLIC,
                    published__isnull=False).get(pk=resource_id)
            except Table.DoesNotExist:
                return None

        else:
            raise RuntimeError()

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


class DoiMetadataOaiAdapter(MetadataOaiAdapter):

    def get_resource(self, record):
        doi = self.strip_identifier_prefix(record.identifier)

        try:
            return Schema.objects.filter(
                metadata_access_level=ACCESS_LEVEL_PUBLIC,
                published__isnull=False
            ).get(doi=doi)
        except Schema.DoesNotExist:
            try:
                return Table.objects.filter(
                    schema__metadata_access_level=ACCESS_LEVEL_PUBLIC,
                    schema__published__isnull=False,
                    metadata_access_level=ACCESS_LEVEL_PUBLIC,
                    published__isnull=False,
                ).get(doi=doi)
            except Schema.DoesNotExist:
                return None

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
