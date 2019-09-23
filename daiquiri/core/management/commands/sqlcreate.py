import socket

from django.conf import settings
from django.core.management.base import BaseCommand


COMMANDS = {
    'django.db.backends.mysql': {
        'default': '''
-- Run the following commands on \'%(HOST)s\':
CREATE USER \'%(USER)s\'@\'%(CLIENT)s\' identified by \'%(PASSWORD)s\';
CREATE DATABASE `%(NAME)s` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
GRANT ALL PRIVILEGES ON `%(NAME)s`.* to \'%(USER)s\'@\'%(CLIENT)s\';
''',
        'data': '''
-- Run the following commands on \'%(HOST)s\':
CREATE USER \'%(USER)s\'@\'%(CLIENT)s\' identified by \'%(PASSWORD)s\';
CREATE DATABASE `%(TAP_SCHEMA)s` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE `%(TAP_UPLOAD)s` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
GRANT ALL PRIVILEGES ON `%(TAP_SCHEMA)s`.* to \'%(USER)s\'@\'%(CLIENT)s\';
GRANT ALL PRIVILEGES ON `%(TAP_UPLOAD)s`.* to \'%(USER)s\'@\'%(CLIENT)s\';
GRANT ALL PRIVILEGES ON `%(PREFIX)s%%`.* to \'%(USER)s\'@\'%(CLIENT)s\';
''',
        'schema': '''
-- Run the following commands on \'%(HOST)s\':
GRANT SELECT ON `%(SCHEMA_NAME)s`.* TO \'%(USER)s\'@\'%(CLIENT)s\';
'''
    },
    'django.db.backends.postgresql': {
        'default': '''
-- Run the following commands on \'%(HOST)s\':
CREATE USER %(USER)s WITH PASSWORD \'%(PASSWORD)s\';
CREATE DATABASE %(NAME)s WITH OWNER %(USER)s;
''',
        'data': '''
-- Run the following commands on \'%(HOST)s\':
CREATE USER %(USER)s WITH PASSWORD \'%(PASSWORD)s\';
CREATE DATABASE %(NAME)s;
GRANT CREATE ON DATABASE %(NAME)s TO %(USER)s;
\\c %(NAME)s
CREATE SCHEMA %(TAP_SCHEMA)s AUTHORIZATION %(USER)s;
CREATE SCHEMA %(TAP_UPLOAD)s AUTHORIZATION %(USER)s;
CREATE SCHEMA %(OAI_SCHEMA)s AUTHORIZATION %(USER)s;
''',
        'schema': '''
-- Run the following commands on %(HOST)s:
\c %(NAME)s
GRANT USAGE ON SCHEMA %(SCHEMA_NAME)s TO %(USER)s;
GRANT SELECT ON ALL TABLES IN SCHEMA %(SCHEMA_NAME)s TO %(USER)s;
'''
    }
}

class Command(BaseCommand):

    requires_system_checks = False
    can_import_settings = True

    def add_arguments(self, parser):
        parser.add_argument('--schema', help='Show commands for a science schema.')
        parser.add_argument('--test', action='store_true', help='Show commands for the test databases.')

    def get_config(self, key):
        config = settings.DATABASES.get(key)

        if config:
            if 'HOST' not in config or not config['HOST'] or config['HOST'] in ['localhost', '127.0.0.1', '::1']:
                config['HOST'] = 'localhost'
                config['CLIENT'] = 'localhost'
            else:
                config['CLIENT'] = socket.gethostname()

            config['PREFIX'] = settings.QUERY_USER_SCHEMA_PREFIX
            config['TAP_SCHEMA'] = settings.TAP_SCHEMA
            config['TAP_UPLOAD'] = settings.TAP_UPLOAD
            config['OAI_SCHEMA'] = settings.OAI_SCHEMA
            config['TEST_NAME'] = 'test_%(NAME)s' % config

        return config

    def handle(self, *args, **options):
        if options['schema']:
            config = self.get_config('data')
            config['SCHEMA_NAME'] = options['schema']
            print(COMMANDS[config['ENGINE']]['schema'] % config)
        else:
            for key in ['default', 'data']:
                config = self.get_config(key)
                print(COMMANDS[config['ENGINE']][key] % config)
