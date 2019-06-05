from django.core.management.base import BaseCommand

from daiquiri.metadata.models import Schema, Table

from daiquiri.oai.models import Record
from daiquiri.oai.utils import update_records


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--delete', action='store_true', help='Delete all records first.')

    def handle(self, *args, **options):

        if options['delete']:
            Record.objects.all().delete()

        for schema in Schema.objects.all():
            update_records(schema)

        for table in Table.objects.all():
            update_records(table)
