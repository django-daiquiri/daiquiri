from daiquiri.core.utils import import_class
from django.conf import settings


def OaiAdapter():
    return import_class(settings.OAI_ADAPTER)()


class BaseOaiAdapter(object):

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
        return getattr(self, '%s_%s_serializer_class' % (metadata_prefix, resource_type))

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
