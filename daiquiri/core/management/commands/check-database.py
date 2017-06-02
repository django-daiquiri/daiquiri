from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db.utils import OperationalError, ProgrammingError

from daiquiri.core.adapter import get_adapter
from daiquiri.metadata.models import Database
from daiquiri.query.utils import get_user_database_name


class Command(BaseCommand):

    def handle(self, *args, **options):
        sql = []

        meta = settings.DATABASES['metadata']
        data = settings.DATABASES['data']

        # check if the permissions for the metadata adapter are ok
        try:
            metadata_adapter = get_adapter('metadata')
        except OperationalError:
            sql.append('CREATE USER \'%(USER)s\'@\'localhost\' IDENTIFIED BY \'%(PASSWORD)s\';' % meta)

        # check if the permissions for the data adapter are ok
        try:
            data_adapter = get_adapter('data')
        except OperationalError:
            sql.append('CREATE USER \'%(USER)s\'@\'localhost\' IDENTIFIED BY \'%(PASSWORD)s\';' % data)

        # check if the permissions for the science databases are ok
        databases = Database.objects.all()

        try:
            for database in databases:
                meta.update({'NAME': database.name})
                data.update({'NAME': database.name})

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

        # check if the permissions for the user databases are ok
        user = User.objects.first()

        try:
            database_name = get_user_database_name(user.username)
            data.update({'NAME': get_user_database_name('%')})

            try:
                data_adapter.fetch_tables(data['NAME'])
            except OperationalError:
                sql.append('GRANT ALL ON `%(NAME)s`.* TO \'%(USER)s\'@\'localhost\';' % data)

        except ProgrammingError:
            pass

        if sql:
            print('Some permissions on the database are missing. Please run:')
            print('')
            for line in sql:
                print('    ' + line)
            print('')
