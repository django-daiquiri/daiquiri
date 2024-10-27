import sys

from django.core.management.base import BaseCommand

from daiquiri.core.adapter import DownloadAdapter
from daiquiri.metadata.models import Table


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('schema', help='the schema for the table to dump')
        parser.add_argument('table', help='the table to dump')
        parser.add_argument('format', help='the format for the dump')

    def handle(self, *args, **options):
        table = Table.objects.filter(schema__name=options['schema']).get(name=options['table'])

        for line in DownloadAdapter().generate(options['format'], options['schema'], options['table'],
                                               table.columns.values()):
            sys.stdout.write(line)
