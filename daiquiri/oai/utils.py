from django.conf import settings

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
    try:
        identifier, datestamp, public = OaiAdapter().get_record(resource)
    except TypeError:
        raise RuntimeError('Could not obtain record for resource %s' % str(resource))

    if public is True:
        for metadata_format in settings.OAI_METADATA_FORMATS:
            try:
                record = Record.objects.get(identifier=identifier, metadata_prefix=metadata_format['prefix'])
            except Record.DoesNotExist:
                record = Record(identifier=identifier, metadata_prefix=metadata_format['prefix'])

            record.datestamp = datestamp
            record.deleted = False
            record.save()
    else:
        delete_records(resource)


def delete_records(resource):
    try:
        identifier, datestamp, public = OaiAdapter().get_record(resource)
    except TypeError:
        raise RuntimeError('Could not obtain record for resource %s' % str(resource))

    for metadata_format in settings.OAI_METADATA_FORMATS:
        try:
            record = Record.objects.get(identifier=identifier, metadata_prefix=metadata_format['prefix'])
            record.datestamp = datestamp
            record.deleted = True
            record.save()
        except Record.DoesNotExist:
            pass
