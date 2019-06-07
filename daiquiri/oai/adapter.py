from django.conf import settings

from daiquiri.core.utils import import_class


def OaiAdapter():
    return import_class(settings.OAI_ADAPTER)()


class BaseOaiAdapter(object):

    def get_identifier_prefix(self):
        return settings.OAI_IDENTIFIER_SCHEMA + settings.OAI_IDENTIFIER_DELIMITER \
            + settings.OAI_IDENTIFIER_REPOSITORY + settings.OAI_IDENTIFIER_DELIMITER

    def get_identifier(self, resource):
        raise NotImplementedError

    def get_resource(self, identifier):
        raise NotImplementedError

    def get_serializer_class(self, identifier):
        raise NotImplementedError

    def get_renderer(self, metadata_prefix):
        renderer_class = next(metadata_format['renderer_class']
                              for metadata_format in settings.OAI_METADATA_FORMATS
                              if metadata_format['prefix'] == metadata_prefix)
        return import_class(renderer_class)()
