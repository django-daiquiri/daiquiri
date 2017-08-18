import sys

from django.core.management.base import BaseCommand

from daiquiri.core.adapter import get_adapter
from daiquiri.metadata.models import Table


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('database', help='the database for the table to dump')
        parser.add_argument('table', help='the table to dump')
        parser.add_argument('format', help='the format for the dump')


    def handle(self, *args, **options):
        table = Table.objects.filter(database__name=options['database']).get(name=options['table'])

        for line in get_adapter().download.generate(options['format'], options['database'], options['table'], {
                'columns': table.columns.values()
            }):
            sys.stdout.write(line)
