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

        tap = settings.DATABASES['tap']
        data = settings.DATABASES['data']

        # check if the permissions for the tap adapter are ok
        try:
            get_adapter('tap')
        except OperationalError:
            sql.append('CREATE USER \'%(USER)s\'@\'localhost\' IDENTIFIED BY \'%(PASSWORD)s\';' % tap)
            sql.append('GRANT ALL ON `%(NAME)s`.* TO \'%(USER)s\'@\'localhost\';' % tap)

        # check if the permissions for the data adapter are ok
        try:
            data_adapter = get_adapter('data')
        except OperationalError:
            sql.append('CREATE USER \'%(USER)s\'@\'localhost\' IDENTIFIED BY \'%(PASSWORD)s\';' % data)
            data.update({'NAME': get_user_database_name(None)})
            sql.append('GRANT ALL ON `%(NAME)s`.* TO \'%(USER)s\'@\'localhost\';' % data)

        # check if the permissions for the science databases are ok
        databases = Database.objects.all()

        try:
            for database in databases:
                data.update({'NAME': database.name})

                try:
                    data_adapter.fetch_tables(data['NAME'])
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
