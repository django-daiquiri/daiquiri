from django.conf import settings

from .mysql import MySQLAdapter


def get_adapter(database_config):
    if database_config in settings.DATABASES:
        if settings.DATABASES[database_config]['ENGINE'] == 'django.db.backends.mysql':
            return MySQLAdapter(database_config)
        else:
            raise Exception('database engine "%s" is not supported (yet)' % settings.DATABASES[database_config]['ENGINE'])
    else:
        raise Exception('no database config named "%s" found in settings.DATABASES' % database_config)
