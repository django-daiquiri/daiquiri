from django.core.management.base import BaseCommand, CommandError
from django.utils.translation import gettext_lazy as _

from daiquiri.core.constants import ACCESS_LEVEL_CHOICES
from daiquiri.metadata.models import Schema


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('schema', help='the schema to be updated')
        parser.add_argument('access_level', help='new access_level and metadata_access_level')

    def handle(self, *args, **options):

        if options['access_level'] not in dict(ACCESS_LEVEL_CHOICES):
            raise CommandError(_('Unknown access_level.'))

        schema = Schema.objects.get(name=options['schema'])
        schema.access_level = options['access_level']
        schema.metadata_access_level = options['access_level']
        schema.save()

        for table in schema.tables.all():
            table.access_level = options['access_level']
            table.metadata_access_level = options['access_level']
            table.save()
