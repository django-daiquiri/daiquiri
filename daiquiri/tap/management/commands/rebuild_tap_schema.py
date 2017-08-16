from django.core.management.base import BaseCommand

from daiquiri.metadata.models import Database
from daiquiri.tap.models import (
    Schema as TapSchema,
    Table as TapTable,
    Column as TapColumn,
)
from daiquiri.tap.handlers import database_updated_handler

class Command(BaseCommand):

    def handle(self, *args, **options):

        TapSchema.objects.all().delete()
        TapTable.objects.all().delete()
        TapColumn.objects.all().delete()

        for database in Database.objects.all():
            database_updated_handler(Database, instance=database)
