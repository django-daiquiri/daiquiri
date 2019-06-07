from datetime import datetime

from django.core.management.base import BaseCommand

from daiquiri.oai.models import Record
from daiquiri.oai.utils import update_records

from daiquiri.oai.adapter import OaiAdapter


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--delete', action='store_true', help='Delete all records first.')

    def handle(self, *args, **options):

        adapter = OaiAdapter()

        if options['delete']:
            Record.objects.all().delete()
        else:
            # mark deleted or unpublished records as deleted
            for record in Record.objects.all():
                ressource = adapter.get_resource(record)
                if ressource is None:
                    record.datestamp = datetime.today()
                    record.deleted = True
                    record.save()

        for ressources in OaiAdapter().get_resources():
            for ressource in ressources:
                update_records(ressource)
