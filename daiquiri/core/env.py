import os
from email.utils import getaddresses
from urllib.parse import urlparse

import dj_database_url


def get(key, default=None):
    return os.getenv(key, default)


def get_bool(key, default=None):
    value = os.getenv(key)
    if value:
        return True if value.lower() in ['1', 't', 'true', 'y', 'yes', 'on'] else False
    else:
        return default

def get_abspath(key, default=None):
    value = os.getenv(key, default)
    return os.path.abspath(value) if value else default


def get_schema(key):
    return os.getenv(key, key.lower())


def get_list(key, default=[]):
    value = os.getenv(key)
    if value:
        return [value.strip() for value in value.split(',')]
    else:
        return default


def get_email_list(key, default=[]):
    return getaddresses(get_list(key, default))


def get_url(key, default='/'):
    value = os.getenv(key, default)
    return value if value.endswith('/') else value + '/'


def get_database(key):
    database_string = os.getenv(f'DATABASE_{key.upper()}')
    if database_string:
        database_type = urlparse(database_string).scheme

        # rewrite mariadb since it is not supported by dj_database_url
        if database_type == 'mariadb':
            database_string = database_string.replace('mariadb://', 'mysql://')

        database_config = dj_database_url.parse(database_string)

        # patch bug in dj_database_url
        if database_type in ['postgres', 'postgresql', 'pgsql']:
            database_config['ENGINE'] = 'django.db.backends.postgresql'

        return database_config

    else:
        return {}


def get_database_adapter():
    database_string = os.getenv('DATABASE_DATA')
    database_type = urlparse(database_string).scheme

    if database_type in ['postgres', 'postgresql', 'pgsql']:
        return 'daiquiri.core.adapter.database.postgres.PostgreSQLAdapter'
    elif database_type == 'mysql':
        return 'daiquiri.core.adapter.database.mysql.MySQLAdapter'
    elif database_type == 'mariadb':
        return 'daiquiri.core.adapter.database.mariadb.MariaDBAdapter'
    else:
        return None


def get_download_adapter():
    database_string = os.getenv('DATABASE_DATA')
    database_type = urlparse(database_string).scheme

    if database_type in ['postgres', 'postgresql', 'pgsql']:
        return 'daiquiri.core.adapter.download.pgdump.PgDumpAdapter'
    elif database_type in ['mysql', 'mariadb']:
        return 'daiquiri.core.adapter.download.mysqldump.MysqldumpAdapter'
    else:
        return None
