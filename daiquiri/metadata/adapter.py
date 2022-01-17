from django.conf import settings
from django.urls import reverse

from daiquiri.core.constants import ACCESS_LEVEL_PUBLIC
from daiquiri.datalink.adapter import BaseDatalinkAdapter, TablesDatalinkAdapterMixin
from daiquiri.oai.adapter import BaseOaiAdapter
from daiquiri.registry.adapter import RegistryOaiAdapterMixin

from .models import Schema, Table
from .serializers.datacite import (DataciteSchemaSerializer,
                                   DataciteTableSerializer)
from .serializers.dublincore import (DublincoreSchemaSerializer,
                                     DublincoreTableSerializer)


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


class MetadataDatalinkAdapterMixin(object):

    def fetch_metadata_rows(self):
        for schema in Schema.objects.all():
            if schema.metadata_access_level == ACCESS_LEVEL_PUBLIC:
                path = reverse('metadata:schema', args=[schema.name])
                identifier = path.lstrip('/') if schema.doi is None else 'doi:{}'.format(schema.doi)
                access_url = settings.SITE_URL.rstrip('/') + path

                yield {
                   'ID': identifier,
                   'access_url': access_url,
                   'service_def': '',
                   'error_message': '',
                   'description': 'Database schema documentation',
                   'semantics': 'https://www.ivoa.net/rdf/datalink/core#documentation',
                   'content_type': 'application/html',
                   'content_length': None
                }

        for table in Table.objects.select_related('schema'):
            if table.metadata_access_level == ACCESS_LEVEL_PUBLIC and \
                    table.schema.metadata_access_level == ACCESS_LEVEL_PUBLIC:
                path = reverse('metadata:table', args=[table.schema.name, table.name])
                identifier = path.lstrip('/') if table.doi is None else 'doi:{}'.format(table.doi)
                access_url = settings.SITE_URL.rstrip('/') + path

                yield {
                   'ID': identifier,
                   'access_url': access_url,
                   'service_def': '',
                   'error_message': '',
                   'description': 'Database table documentation',
                   'semantics': 'https://www.ivoa.net/rdf/datalink/core#documentation',
                   'content_type': 'application/html',
                   'content_length': None
                }


class MetadataDatalinkAdapter(MetadataDatalinkAdapterMixin, TablesDatalinkAdapterMixin, BaseDatalinkAdapter):

    def fetch_rows(self):
        for row in self.fetch_tables_rows():
            yield row

        for row in self.fetch_metadata_rows():
            yield row
