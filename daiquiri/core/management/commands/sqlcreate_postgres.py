import socket

from django.conf import settings
from django.core.management.base import BaseCommand

# TODO: test!
class Command(BaseCommand):

    requires_system_checks = False
    can_import_settings = True

    def add_arguments(self, parser):
        parser.add_argument('--schema', help='Show commands for a science schema.')
        parser.add_argument('--test', action='store_true', help='Show commands for the test schema.')

    def get_config(self, key):
        config = settings.DATABASES.get(key)

        if config:
            if 'HOST' not in config or not config['HOST']:
                config['HOST'] = 'localhost'
                config['CLIENT'] = 'localhost'
            else:
                config['CLIENT'] = socket.gethostname()

            config['PREFIX'] = settings.QUERY_USER_SCHEMA_PREFIX

        return config

    def handle(self, *args, **options):

        default = self.get_config('default')
        tap = self.get_config('tap')
        data = self.get_config('data')

        print('')

        if options['schema']:
            if data:
                data.update({'SCHEMA_NAME': options['schema']})
                print('''-- Run the following commands on \'%(HOST)s\':
GRANT SELECT ON "%(schema_NAME)s".* to \'%(USER)s\'@\'%(CLIENT)s\';''' % data)
            else:
                raise RuntimeError('No \'data\' SCHEMA connection configured.')

        elif options['test']:

            if default:
                print('''-- For testing, run the following commands on \'%(HOST)s\':
GRANT ALL PRIVILEGES ON "test_%(NAME)s".* to \'%(USER)s\'@\'%(CLIENT)s\';
''' % default)

            if tap:
                print('''-- For testing, run the following commands on \'%(HOST)s\':
GRANT ALL PRIVILEGES ON "test_%(NAME)s".* to \'%(USER)s\'@\'%(CLIENT)s\';
''' % tap)

            if data:
                print('''-- For testing, run the following commands on \'%(HOST)s\':
GRANT ALL PRIVILEGES ON "test_".* to \'%(USER)s\'@\'%(CLIENT)s\';
''' % data)

        else:

            if default:
                print('''-- Run the following commands on \'%(HOST)s\':
CREATE SCHEMA "%(NAME)s";
CREATE USER \'%(USER)s\'@\'%(CLIENT)s\' WITH PASSWORD \'%(PASSWORD)s\';
GRANT ALL PRIVILEGES ON "%(NAME)s".* to \'%(USER)s\'@\'%(CLIENT)s\';
''' % default)

            if tap:
                print('''-- Run the following commands on \'%(HOST)s\':
CREATE SCHEMA "%(NAME)s";
CREATE USER \'%(USER)s\'@\'%(CLIENT)s\' WITH PASSWORD \'%(PASSWORD)s\';
GRANT ALL PRIVILEGES ON "%(NAME)s".* to \'%(USER)s\'@\'%(CLIENT)s\';
''' % tap)

            if data:
                print('''-- Run the following commands on \'%(HOST)s\':
CREATE USER \'%(USER)s\'@\'%(CLIENT)s\' WITH PASSWORD \'%(PASSWORD)s\';
GRANT ALL PRIVILEGES ON "%(PREFIX)s%%".* to \'%(USER)s\'@\'%(CLIENT)s\';''' % data)
                if tap:
                    data.update({'SCHEMA_NAME': tap['NAME']})
                    print('GRANT SELECT ON "%(SCHEMA_NAME)s".* to \'%(USER)s\'@\'%(CLIENT)s\';' % data)

        print('')
