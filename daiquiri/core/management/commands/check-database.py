from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.utils import OperationalError, ProgrammingError

from daiquiri.core.adapter import get_adapter
from daiquiri.metadata.models import Database


class Command(BaseCommand):

    def handle(self, *args, **options):
        sql = []

        meta = settings.DATABASES['metadata']
        data = settings.DATABASES['data']

        try:
            metadata_adapter = get_adapter('metadata')
        except OperationalError:
            sql.append('CREATE USER \'%(USER)s\'@\'localhost\' IDENTIFIED BY \'%(PASSWORD)s\';' % meta)

        try:
            data_adapter = get_adapter('data')
        except OperationalError:
            sql.append('CREATE USER \'%(USER)s\'@\'localhost\' IDENTIFIED BY \'%(PASSWORD)s\';' % data)

        # try:
        databases = Database.objects.values_list()

        try:
            for row in databases:
                meta.update({'NAME': row[2]})
                data.update({'NAME': row[2]})

                try:
                    metadata_adapter.fetch_tables(meta['NAME'])
                except OperationalError:
                    sql.append('GRANT SELECT, ALTER ON `%(NAME)s`.* TO \'%(USER)s\'@\'localhost\';' % meta)

                try:
                    data_adapter.fetch_tables(meta['NAME'])
                except OperationalError:
                    sql.append('GRANT SELECT ON `%(NAME)s`.* TO \'%(USER)s\'@\'localhost\';' % data)

        except ProgrammingError:
            pass

        if sql:
            print('Some permissions on the database are missing. Please run:')
            print('')
            for line in sql:
                print('    ' + line)
            print('')
