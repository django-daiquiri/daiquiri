from django.conf import settings

from daiquiri.oai.adapter import BaseOaiAdapter

from .models import Schema, Table
from .serializers.datacite import SchemaDataciteSerializer, TableDataciteSerializer
from .serializers.dublincore import SchemaDublincoreSerializer, TableDublincoreSerializer


class MetadataOaiAdapter(BaseOaiAdapter):

    prefix = settings.OAI_IDENTIFIER_PREFIX

    def get_prefix(self):
        return settings.OAI_IDENTIFIER_PREFIX

    def get_identifier(self, resource):

        if isinstance(resource, Schema):
            return self.prefix + 'schemas/%i' % resource.pk

        elif isinstance(resource, Table):
            return self.prefix + 'tables/%i' % resource.pk

        else:
            return None

        raise NotImplementedError

    def get_resource(self, identifier):
        if identifier.startswith(self.prefix):
            resource_type, resource_id = identifier[len(self.prefix):].split('/')

            if resource_type == 'schemas':
                return Schema.objects.get(pk=resource_id)

            elif resource_type == 'tables':
                return Table.objects.get(pk=resource_id)

            else:
                raise RuntimeError()
        else:
            return None

    def get_serializer_class(self, resource, metadata_prefix):
        if isinstance(resource, Schema):
            if metadata_prefix == 'oai_dc':
                return SchemaDublincoreSerializer
            elif metadata_prefix == 'oai_datacite':
                return SchemaDataciteSerializer
            else:
                raise RuntimeError('metadata_prefix not supported')

        elif isinstance(resource, Table):
            if metadata_prefix == 'oai_dc':
                return TableDublincoreSerializer
            elif metadata_prefix == 'oai_datacite':
                return TableDataciteSerializer
            else:
                raise RuntimeError('metadata_prefix not supported')

        else:
            raise RuntimeError('resource_type not supported')
