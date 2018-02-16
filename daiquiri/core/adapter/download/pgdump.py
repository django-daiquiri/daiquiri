import logging

from .base import DownloadAdapter

logger = logging.getLogger(__name__)


class PgDumpAdapter(DownloadAdapter):

    FORMATS = {
        'char': 'c',
        'unsignedByte': 'B',
        'short': 'h',
        'int': 'i',
        'long': 'q',
        'float': 'f',
        'double': 'd',
        'spoint': None
    }

    NULL_VALUES = {
        'char': '',
        'unsignedByte': 255,
        'short': 32767,
        'int': 2147483647,
        'long': 9223372036854775807,
        'float': float('nan'),
        'double': float('nan')
    }

    def set_args(self, schema_name, table_name):
        # command line for pg_dump:
        # pg_dump -a --inserts --dbname=postgresql://user:password@host:port/database --table=schema.table

        dbname_string = '--dbname=postgresql://'

        if 'USER' in self.database_config and self.database_config['USER']:
            dbname_string += '%(USER)s' % self.database_config

        if 'PASSWORD' in self.database_config and self.database_config['PASSWORD']:
            dbname_string +=':%(PASSWORD)s' % self.database_config

        if 'HOST' in self.database_config and self.database_config['HOST']:
            dbname_string +='@%(HOST)s' % self.database_config

        if 'PORT' in self.database_config and self.database_config['PORT']:
            dbname_string +=':%(PORT)s' % self.database_config

        if 'NAME' in self.database_config and self.database_config['NAME']:
            dbname_string +='/%(NAME)s' % self.database_config

        self.args = ['pg_dump', '-a', '--inserts', dbname_string, '--table=%s.%s' % (schema_name, table_name)]
