import logging

from django.conf import settings

from daiquiri.core.utils import import_class

from .adapter import OaiAdapter
from .models import Record

logger = logging.getLogger(__name__)


def get_metadata_format(metadata_prefix):
    return next(metadata_format for metadata_format in settings.OAI_METADATA_FORMATS
                if metadata_format['prefix'] == metadata_prefix)


def get_renderer(metadata_prefix):
    renderer_class = get_metadata_format(metadata_prefix)['renderer_class']
    return import_class(renderer_class)()


def update_records(resource_type, resource):
    logger.debug('update_records %s %s', resource_type, resource)

    adapter = OaiAdapter()

    if resource_type in adapter.resource_types:
        try:
            resource_id, identifier, datestamp, set_spec, public = adapter.get_record(resource_type, resource)
        except TypeError as e:
            raise RuntimeError(f'Could not obtain record for {resource_type} {resource}') from e

        if public is True:
            for metadata_prefix in adapter.get_metadata_prefixes(resource_type):
                try:
                    record = Record.objects.get(identifier=identifier, metadata_prefix=metadata_prefix)
                except Record.DoesNotExist:
                    record = Record(identifier=identifier, metadata_prefix=metadata_prefix)

                record.datestamp = datestamp
                record.set_spec = set_spec
                record.deleted = False
                record.resource_type = resource_type
                record.resource_id = resource_id
                record.save()
        else:
            delete_records(resource_type, resource)


def delete_records(resource_type, resource):
    logger.debug('delete_records %s %s', resource_type, resource)

    adapter = OaiAdapter()

    if resource_type in adapter.resource_types:
        try:
            resource_id, identifier, datestamp, set_spec, public = adapter.get_record(resource_type, resource)
        except TypeError as e:
            raise RuntimeError(f'Could not obtain record for {resource_type} {resource}') from e

        for metadata_prefix in adapter.get_metadata_prefixes(resource_type):
            try:
                record = Record.objects.get(identifier=identifier, metadata_prefix=metadata_prefix)
                record.datestamp = datestamp
                record.set_spec = set_spec
                record.deleted = True
                record.save()
            except Record.DoesNotExist:
                pass
