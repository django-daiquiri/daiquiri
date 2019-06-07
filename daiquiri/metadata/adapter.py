from daiquiri.core.constants import ACCESS_LEVEL_PUBLIC
from daiquiri.oai.adapter import BaseOaiAdapter

from .models import Schema, Table
from .serializers.datacite import SchemaDataciteSerializer, TableDataciteSerializer
from .serializers.dublincore import SchemaDublincoreSerializer, TableDublincoreSerializer


class MetadataOaiAdapter(BaseOaiAdapter):

    def get_record(self, resource):
        prefix = self.get_identifier_prefix()

        if isinstance(resource, Schema):
            identifier = prefix + 'schemas/%i' % resource.pk
            datestamp = resource.updated or resource.published
            public = (resource.metadata_access_level == ACCESS_LEVEL_PUBLIC) \
                and (resource.published is not None)
        elif isinstance(resource, Table):
            identifier = prefix + 'tables/%i' % resource.pk
            datestamp = resource.updated or resource.published
            public = (resource.metadata_access_level == ACCESS_LEVEL_PUBLIC) \
                and (resource.published is not None) \
                and (resource.schema.metadata_access_level == ACCESS_LEVEL_PUBLIC) \
                and (resource.schema.published is not None)

        else:
            raise RuntimeError('Unsupported resource')

        return identifier, datestamp, public

    def get_resource(self, record):
        prefix = self.get_identifier_prefix()

        if record.identifier.startswith(prefix):
            resource_type, resource_id = record.identifier[len(prefix):].split('/')

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
