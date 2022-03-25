from datetime import datetime

from django.core.management.base import BaseCommand

from daiquiri.oai.adapter import OaiAdapter
from daiquiri.oai.models import Record
from daiquiri.oai.utils import update_records


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--resource_type', default=None, help='Update only a specific resource type.')
        parser.add_argument('--delete', action='store_true', help='Delete all records first.')

    def handle(self, *args, **options):

        adapter = OaiAdapter()

        if options['delete']:
            # delete and bulk ingest all records
            Record.objects.all().delete()

            records = []
            for resource_type, resource in adapter.get_resource_list():
                if options['resource_type'] in [None, resource_type]:
                    resource_id, identifier, datestamp, set_spec, public = adapter.get_record(resource_type, resource)

                    if public is True:
                        for metadata_prefix in adapter.get_metadata_prefixes(resource_type):
                            records.append(Record(
                                identifier=identifier,
                                metadata_prefix=metadata_prefix,
                                datestamp=datestamp,
                                set_spec=set_spec,
                                deleted=False,
                                resource_type=resource_type,
                                resource_id=resource_id
                            ))

            Record.objects.bulk_create(records)
        else:
            # mark deleted or unpublished records as deleted
            for record in Record.objects.all():
                resource = adapter.get_resource(record)
                if resource is None:
                    record.datestamp = datetime.today()
                    record.deleted = True
                    record.save()

            # update records one by one
            for resource_type, resource in adapter.get_resource_list():
                if options['resource_type'] in [None, resource_type]:
                    update_records(resource_type, resource)
