from django.conf import settings

from daiquiri.core.utils import import_class
from daiquiri.metadata.models import Schema, Table


def OaiAdapter():
    return import_class(settings.OAI_ADAPTER)()


class BaseOaiAdapter(object):

    def get_resource(self, identifier):
        raise NotImplementedError

    def get_identifier(self, resource):
        raise NotImplementedError


class SimpleOaiAdapter(object):

    def get_prefix(self):
        return settings.OAI_IDENTIFIER_PREFIX

    def get_resource(self, identifier):
        resource_type, resource_id = identifier.split('/')

        if resource_type == 'schemas':
            return Schema.objects.get(pk=resource_id)

        elif resource_type == 'tables':
            return Table.objects.get(pk=resource_id)

        else:
            return None

    def get_identifier(self, resource):

        if isinstance(resource, Schema):
            return self.get_prefix() + 'schemas/%i' % resource.pk

        elif isinstance(resource, Table):
            return self.get_prefix() + 'tables/%i' % resource.pk

        else:
            return None

        raise NotImplementedError
