from django.apps import apps
from django.conf import settings

from .serializers import DublincoreSerializer, VoresourceSerializer


class RegistryOaiAdapterMixin(object):

    oai_dc_service_serializer_class = DublincoreSerializer
    ivo_vor_service_serializer_class = VoresourceSerializer

    services = ['registry', 'authority', 'web', 'tap', 'conesearch']

    def get_service_list(self):
        for i, service in enumerate(self.services):
            yield 'service', self.get_service(i + 1)

    def get_service(self, pk):
        index = pk - 1

        if self.services[index] == 'registry':
            from daiquiri.registry.vo import get_resource
            return get_resource()
        elif self.services[index] == 'authority':
            from daiquiri.registry.vo import get_authority_resource
            return get_authority_resource()
        elif self.services[index] == 'web':
            from daiquiri.registry.vo import get_web_resource
            return get_web_resource()
        elif self.services[index] == 'tap' and apps.is_installed('daiquiri.tap'):
            from daiquiri.tap.vo import get_resource
            return get_resource()
        elif self.services[index] == 'conesearch' and apps.is_installed('daiquiri.conesearch'):
            from daiquiri.conesearch.vo import get_resource
            return get_resource()

    def get_service_record(self, service):
        index = self.services.index(service['service']) + 1
        identifier = self.get_identifier(service['service'])
        datestamp = settings.SITE_UPDATED
        public = True

        return index, identifier, datestamp, public
