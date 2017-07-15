from django.conf import settings

from .database.mysql import MySQLAdapter
from .download.mysqldump import MysqldumpAdapter

_adapter = None


class Adapter(object):

    database_key = 'data'

    def __init__(self):

        if self.database_key in settings.DATABASES:
            database_config = settings.DATABASES[self.database_key]

            if database_config['ENGINE'] == 'django.db.backends.mysql':
                self.database = MySQLAdapter(self.database_key, database_config)
                self.download = MysqldumpAdapter(self.database_key, database_config)
            else:
                raise Exception('database engine "%s" is not supported (yet)' % database_config['ENGINE'])
        else:
            raise Exception('no database config named "%s" found in settings.DATABASES' % self.database_key)


def get_adapter():
    global _adapter
    if not _adapter:
        _adapter = Adapter()

    return _adapter
