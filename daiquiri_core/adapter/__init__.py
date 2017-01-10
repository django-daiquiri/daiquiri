from django.conf import settings

from .mysql import MySQLAdapter


def get_adapter(database_key):
    if database_key in settings.DATABASES:
        database_config = settings.DATABASES[database_key]
        if database_config['ENGINE'] == 'django.db.backends.mysql':
            return MySQLAdapter(database_key, database_config)
        else:
            raise Exception('database engine "%s" is not supported (yet)' % database_config['ENGINE'])
    else:
        raise Exception('no database config named "%s" found in settings.DATABASES' % database_key)
