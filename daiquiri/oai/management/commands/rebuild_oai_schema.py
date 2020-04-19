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
            Record.objects.all().delete()
        else:
            # mark deleted or unpublished records as deleted
            for record in Record.objects.all():
                resource = adapter.get_resource(record)
                if resource is None:
                    record.datestamp = datetime.today()
                    record.deleted = True
                    record.save()

        for resource_type, resource in OaiAdapter().get_resource_list():
            if options['resource_type'] in [None, resource_type]:
                update_records(resource_type, resource)
