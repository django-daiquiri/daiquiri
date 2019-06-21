from django.conf import settings

from daiquiri.core.utils import import_class


def OaiAdapter():
    return import_class(settings.OAI_ADAPTER)()


class BaseOaiAdapter(object):

    resource_types = {}

    def get_resource_list(self):
        for resource_type in self.resource_types:
            yield from getattr(self, 'get_%s_list' % resource_type)()

    def get_resource(self, record):
        return getattr(self, 'get_%s' % record.resource_type)(record.resource_id)

    def get_record(self, resource_type, resource):
        return getattr(self, 'get_%s_record' % resource_type)(resource)

    def get_serializer_class(self, metadata_prefix, resource_type):
        return getattr(self, 'get_%s_%s_serializer_class' % (metadata_prefix, resource_type))()

    def get_renderer(self, metadata_prefix):
        renderer_class = next(metadata_format['renderer_class']
                              for metadata_format in settings.OAI_METADATA_FORMATS
                              if metadata_format['prefix'] == metadata_prefix)
        return import_class(renderer_class)()

    def get_identifier_prefix(self):
        return settings.OAI_IDENTIFIER_SCHEMA + settings.OAI_IDENTIFIER_DELIMITER \
            + settings.OAI_IDENTIFIER_REPOSITORY + settings.OAI_IDENTIFIER_DELIMITER

    def strip_identifier_prefix(self, identifier):
        prefix = self.get_identifier_prefix()

        if identifier.startswith(prefix):
            return identifier[len(prefix):]
        else:
            raise RuntimeError('Wrong prefix')
