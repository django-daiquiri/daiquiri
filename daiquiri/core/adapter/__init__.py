from django.conf import settings

from daiquiri.core.utils import import_class

from .database.mysql import MySQLAdapter
from .download.mysqldump import MysqldumpAdapter

_adapter = None


class Adapter(object):

    def __init__(self):

        self.database_key = 'data'
        self.database_config = settings.DATABASES['data']

        try:
            database_adapter_class = import_class(settings.ADAPTER_DATABASE)
            self.database = database_adapter_class(self.database_key, self.database_config)
        except AttributeError:

            if self.database_config['ENGINE'] == 'django.db.backends.mysql':
                self.database = MySQLAdapter(self.database_key, self.database_config)
            else:
                raise Exception('No suitable database adapter found.')

        try:
            download_adapter_class = import_class(settings.ADAPTER_DOWNLOAD)
            self.download = download_adapter_class(self.database_key, self.database_config)
        except AttributeError:

            if self.database_config['ENGINE'] == 'django.db.backends.mysql':
                self.download = MysqldumpAdapter(self.database_key, self.database_config)
            else:
                raise Exception('No suitable download adapter found.')


def get_adapter():
    global _adapter
    if not _adapter:
        _adapter = Adapter()

    return _adapter
