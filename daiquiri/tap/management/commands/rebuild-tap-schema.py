from django.core.management.base import BaseCommand

from daiquiri.metadata.models import Database

class Command(BaseCommand):

    def handle(self, *args, **options):
        for database in Database.objects.all():
            print database
            database.save()

            for table in database.tables.all():
                print ' ', table
                table.save()

                for column in table.columns.all():
                    print '   ', column
                    column.save()
