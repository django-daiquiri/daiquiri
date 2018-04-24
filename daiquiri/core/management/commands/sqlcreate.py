import socket

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    requires_system_checks = False
    can_import_settings = True

    def add_arguments(self, parser):
        parser.add_argument('--schema', help='Show commands for a science schema.')
        parser.add_argument('--test', action='store_true', help='Show commands for the test databases.')

    def get_config(self, key):
        config = settings.DATABASES.get(key)

        if config:
            if 'HOST' not in config or not config['HOST']:
                config['HOST'] = 'localhost'
                config['CLIENT'] = 'localhost'
            else:
                config['CLIENT'] = socket.gethostname()

            config['PREFIX'] = settings.QUERY_USER_SCHEMA_PREFIX
            config['TAP_SCHEMA'] = settings.TAP_SCHEMA
            config['TEST_NAME'] = 'test_%(NAME)s' % config

        return config

    def handle(self, *args, **options):

        config = {key: self.get_config(key) for key in ['default', 'data']}

        print('')

        if options['schema']:
            if config['data']:
                if config['data']['ENGINE'] == 'django.db.backends.mysql':
                    config['data'].update({'SCHEMA_NAME': options['schema']})
                    print('''-- Run the following commands on \'%(HOST)s\':
GRANT SELECT ON `%(SCHEMA_NAME)s`.* TO \'%(USER)s\'@\'%(CLIENT)s\';
''' % config['data'])
                elif config['data']['ENGINE'] == 'django.db.backends.postgresql':
                    config['data'].update({'SCHEMA_NAME': options['schema']})
                    print('''-- Run the following commands on %(HOST)s:
\c %(NAME)s
GRANT USAGE ON SCHEMA %(SCHEMA_NAME)s TO %(USER)s;
GRANT SELECT ON ALL TABLES IN SCHEMA %(SCHEMA_NAME)s TO %(USER)s;
''' % config['data'])

            else:
                raise RuntimeError('No \'data\' database connection configured.')

        elif options['test']:
            if config['default']:
                if config['default']['ENGINE'] == 'django.db.backends.mysql':
                    print('''-- For testing, run the following commands on \'%(HOST)s\':
CREATE DATABASE `%(TEST_NAME)s` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
GRANT ALL PRIVILEGES ON `%(TEST_NAME)s`.* to \'%(USER)s\'@\'%(CLIENT)s\';
''' % config['default'])

                elif config['default']['ENGINE'] == 'django.db.backends.postgresql':
                    print('''-- Run the following commands on \'%(HOST)s\':
CREATE DATABASE %(TEST_NAME)s WITH OWNER %(USER)s;
''' % config['default'])

            if config['data']:
                if config['data']['ENGINE'] == 'django.db.backends.mysql':
                    print('''-- For testing, run the following commands on \'%(HOST)s\':
CREATE DATABASE `%(TEST_NAME)s`;
GRANT ALL PRIVILEGES ON `%(TEST_NAME)s`.* to \'%(USER)s\'@\'%(CLIENT)s\';
''' % config['data'])

                elif config['data']['ENGINE'] == 'django.db.backends.postgresql':
                    print('''-- Run the following commands on \'%(HOST)s\':
CREATE DATABASE %(TEST_NAME)s WITH OWNER %(USER)s;
\c %(TEST_NAME)s
CREATE SCHEMA %(TAP_SCHEMA)s AUTHORIZATION %(USER)s;
''' % config['data'])

        else:
            if config['default']:
                if config['default']['ENGINE'] == 'django.db.backends.mysql':
                    print('''-- Run the following commands on \'%(HOST)s\':
CREATE USER \'%(USER)s\'@\'%(CLIENT)s\' identified by \'%(PASSWORD)s\';
CREATE DATABASE `%(NAME)s` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
GRANT ALL PRIVILEGES ON `%(NAME)s`.* to \'%(USER)s\'@\'%(CLIENT)s\';
''' % config['default'])

                elif config['default']['ENGINE'] == 'django.db.backends.postgresql':
                    print('''-- Run the following commands on \'%(HOST)s\':
CREATE USER %(USER)s WITH PASSWORD \'%(PASSWORD)s\';
CREATE DATABASE %(NAME)s WITH OWNER %(USER)s;
''' % config['default'])

            if config['data']:
                if config['data']['ENGINE'] == 'django.db.backends.mysql':
                    print('''-- Run the following commands on \'%(HOST)s\':
CREATE USER \'%(USER)s\'@\'%(CLIENT)s\' identified by \'%(PASSWORD)s\';
GRANT ALL PRIVILEGES ON `%(TAP_SCHEMA)s`.* to \'%(USER)s\'@\'%(CLIENT)s\';
GRANT ALL PRIVILEGES ON `%(PREFIX)s%%`.* to \'%(USER)s\'@\'%(CLIENT)s\';
''' % config['data'])

                elif config['data']['ENGINE'] == 'django.db.backends.postgresql':
                    print('''-- Run the following commands on \'%(HOST)s\':
CREATE USER %(USER)s WITH PASSWORD \'%(PASSWORD)s\';
CREATE DATABASE %(NAME)s;
GRANT CREATE ON DATABASE %(NAME)s TO %(USER)s;
\c %(NAME)s
CREATE SCHEMA %(TAP_SCHEMA)s AUTHORIZATION %(USER)s;
''' % config['data'])
