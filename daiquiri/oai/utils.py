from django.conf import settings

from daiquiri.core.constants import ACCESS_LEVEL_PUBLIC

from .models import Record
from .adapter import OaiAdapter


def update_records(resource):
    if resource.metadata_access_level == ACCESS_LEVEL_PUBLIC and resource.published:

        identifier = OaiAdapter().get_identifier(resource)

        for metadata_prefix in settings.OAI_METADATA_PREFIX:
            try:
                record = Record.objects.get(identifier=identifier, metadata_prefix=metadata_prefix)
            except Record.DoesNotExist:
                record = Record(identifier=identifier, metadata_prefix=metadata_prefix)

            record.datestamp = resource.updated or resource.published
            record.deleted = False
            record.save()

    else:
        delete_records(resource)


def delete_records(resource):
    identifier = OaiAdapter().get_identifier(resource)

    for metadata_prefix in settings.OAI_METADATA_PREFIX:
        try:
            record = Record.objects.get(identifier=identifier, metadata_prefix=metadata_prefix)
            record.deleted = True
            record.save()
        except Record.DoesNotExist:
            pass
