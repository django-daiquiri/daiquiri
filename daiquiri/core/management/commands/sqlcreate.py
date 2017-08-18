import socket

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.utils import OperationalError, ProgrammingError

from daiquiri.metadata.models import Database


class Command(BaseCommand):

    requires_system_checks = False
    can_import_settings = True

    def get_config(self, key):
        config = settings.DATABASES.get(key)

        if 'HOST' not in config or not config['HOST']:
            config['HOST'] = 'localhost'
            config['CLIENT'] = 'localhost'
        else:
            config['CLIENT'] = socket.gethostname()

        config['PREFIX'] = settings.QUERY_USER_DATABASE_PREFIX

        return config

    def handle(self, *args, **options):

        default = self.get_config('default')
        tap = self.get_config('tap')
        data = self.get_config('data')

        print('''-- Run the following commands on \'%(HOST)s\':

CREATE DATABASE `%(NAME)s`;
CREATE USER \'%(USER)s\'@\'%(CLIENT)s\' identified by \'%(PASSWORD)s\';
GRANT ALL PRIVILEGES ON `%(NAME)s`.* to \'%(USER)s\'@\'%(CLIENT)s\';
''' % default)

        print('''-- Run the following commands on \'%(HOST)s\':

CREATE DATABASE `%(NAME)s`;
CREATE USER \'%(USER)s\'@\'%(CLIENT)s\' identified by \'%(PASSWORD)s\';
GRANT ALL PRIVILEGES ON `%(NAME)s`.* to \'%(USER)s\'@\'%(CLIENT)s\';
''' % tap)

        print('''-- Run the following commands on \'%(HOST)s\':

CREATE USER \'%(USER)s\'@\'%(CLIENT)s\' identified by \'%(PASSWORD)s\';
GRANT ALL PRIVILEGES ON `%(PREFIX)s%%`.* to \'%(USER)s\'@\'%(CLIENT)s\';
''' % data)

        try:
            for database in Database.objects.all():
                data.update({'DATABASE_NAME': database.name})
                print('GRANT SELECT ON `%(DATABASE_NAME)s`.* to \'%(USER)s\'@\'%(CLIENT)s\';' % data)
        except (OperationalError, ProgrammingError):
            pass
        else:
            print('')

        print('''-- For testing, run the following commands on \'%(HOST)s\':

GRANT ALL PRIVILEGES ON `test_%(NAME)s`.* to \'%(USER)s\'@\'%(CLIENT)s\';
''' % default)

        print('''-- For testing, run the following commands on \'%(HOST)s\':

GRANT ALL PRIVILEGES ON `test_%(NAME)s`.* to \'%(USER)s\'@\'%(CLIENT)s\';
''' % tap)

        print('''-- For testing, run the following commands on \'%(HOST)s\':

GRANT ALL PRIVILEGES ON `test_`.* to \'%(USER)s\'@\'%(CLIENT)s\';
''' % data)
