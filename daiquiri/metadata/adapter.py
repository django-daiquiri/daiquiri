from django.conf import settings
from django.urls import reverse

from daiquiri.core.constants import ACCESS_LEVEL_PUBLIC
from daiquiri.core.utils import get_doi_url
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

    def get_schema_list(self):
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
               'description': 'Database schema documentation',
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
                   'description': 'Digital object identifier',
                   'semantics': '#doi',
                   'content_type': 'application/html',
                   'content_length': None
                })

        return schema_links

    def get_table_list(self):
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
               'description': 'Database table documentation',
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
                   'description': 'Digital object identifier',
                   'semantics': '#doi',
                   'content_type': 'application/html',
                   'content_length': None
                })

        return table_links


class MetadataDatalinkAdapter(MetadataDatalinkAdapterMixin, TablesDatalinkAdapterMixin, BaseDatalinkAdapter):

    resource_types = ['datalink', 'schema', 'table']
