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
CREATE DATABASE `%(NAME)s` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE `%(TAP_SCHEMA)s` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE `%(TAP_UPLOAD)s` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE `%(OAI_SCHEMA)s` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
GRANT SELECT ON `%(NAME)s`.* to \'%(USER)s\'@\'%(CLIENT)s\';
GRANT ALL PRIVILEGES ON `%(TAP_SCHEMA)s`.* to \'%(USER)s\'@\'%(CLIENT)s\';
GRANT ALL PRIVILEGES ON `%(TAP_UPLOAD)s`.* to \'%(USER)s\'@\'%(CLIENT)s\';
GRANT ALL PRIVILEGES ON `%(OAI_SCHEMA)s`.* to \'%(USER)s\'@\'%(CLIENT)s\';
GRANT ALL PRIVILEGES ON `%(PREFIX)s%%`.* to \'%(USER)s\'@\'%(CLIENT)s\';
''',
        'schema': '''
-- Run the following commands on \'%(HOST)s\':
GRANT SELECT ON `%(SCHEMA_NAME)s`.* TO \'%(USER)s\'@\'%(CLIENT)s\';
''',
        'datalink': '''
-- Run the following commands on %(HOST)s:
CREATE TABLE %(TABLE_NAME)s (
  `datalink_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `ID` varchar(256) NOT NULL,
  `access_url` varchar(256),
  `service_def` varchar(80),
  `error_message` varchar(256),
  `description` varchar(256),
  `semantics` varchar(80) NOT NULL,
  `content_type` varchar(80),
  `content_length` bigint(20),
  PRIMARY KEY (`link_id`)
);
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
\\c %(NAME)s
GRANT USAGE ON SCHEMA %(SCHEMA_NAME)s TO %(USER)s;
GRANT SELECT ON ALL TABLES IN SCHEMA %(SCHEMA_NAME)s TO %(USER)s;
''',
        'datalink': '''
-- Run the following commands on %(HOST)s:
CREATE TABLE %(TABLE_NAME)s (
    datalink_id serial PRIMARY KEY,
    "ID" character varying(256) NOT NULL,
    access_url character varying(256),
    service_def character varying(80),
    error_message character varying(256),
    description character varying(256),
    semantics character varying(80) NOT NULL,
    content_type character varying(80),
    content_length bigint
);
'''
    }
}


class Command(BaseCommand):

    requires_system_checks = []
    can_import_settings = True

    def add_arguments(self, parser):
        parser.add_argument('--schema', help='Show commands for a science schema.')
        parser.add_argument('--datalink', help='Show commands for a datalink table.')

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

        return config

    def handle(self, *args, **options):
        if options['schema']:
            config = self.get_config('data')
            config['SCHEMA_NAME'] = options['schema']
            print(COMMANDS[config['ENGINE']]['schema'] % config)
        elif options['datalink']:
            config = self.get_config('data')
            config['TABLE_NAME'] = options['datalink']
            print(COMMANDS[config['ENGINE']]['datalink'] % config)
        else:
            for key in ['default', 'data']:
                config = self.get_config(key)
                if config:
                    print(COMMANDS[config['ENGINE']][key] % config)
