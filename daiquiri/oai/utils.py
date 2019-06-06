from django.conf import settings

from daiquiri.core.constants import ACCESS_LEVEL_PUBLIC
from daiquiri.core.utils import import_class

from .models import Record
from .adapter import OaiAdapter


def get_metadata_format(metadata_prefix):
    return next(metadata_format for metadata_format in settings.OAI_METADATA_FORMATS
                if metadata_format['prefix'] == metadata_prefix)


def get_renderer(metadata_prefix):
    renderer_class = get_metadata_format(metadata_prefix)['renderer_class']
    return import_class(renderer_class)()


def update_records(resource):
    if resource.metadata_access_level == ACCESS_LEVEL_PUBLIC and resource.published:

        identifier = OaiAdapter().get_identifier(resource)

        for metadata_format in settings.OAI_METADATA_FORMATS:
            try:
                record = Record.objects.get(identifier=identifier, metadata_prefix=metadata_format['prefix'])
            except Record.DoesNotExist:
                record = Record(identifier=identifier, metadata_prefix=metadata_format['prefix'])

            record.datestamp = resource.updated or resource.published
            record.deleted = False
            record.save()

    else:
        delete_records(resource)


def delete_records(resource):
    identifier = OaiAdapter().get_identifier(resource)

    for metadata_format in settings.OAI_METADATA_FORMATS:
        try:
            record = Record.objects.get(identifier=identifier, metadata_prefix=metadata_format['prefix'])
            record.deleted = True
            record.save()
        except Record.DoesNotExist:
            pass
