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
        # pg_dump -a --inserts --user=user --host=host --port=port --dbname=database --table=schema.table

        self.args = ['pg_dump', '-a', '--inserts']

        if 'PASSWORD' in self.database_config and self.database_config['PASSWORD']:
            if 'PORT' in self.database_config and self.database_config['PORT']:
                dbname = '--dbname=postgresql://%(USER)s:%(PASSWORD)s@%(HOST)s:%(PORT)s/'
            else:
                dbname = '--dbname=postgresql://%(USER)s:%(PASSWORD)s@%(HOST)s/'

            self.args.append(dbname % self.database_config)
        else:
            if 'USER' in self.database_config and self.database_config['USER']:
                self.args.append('--user=%(USER)s' % self.database_config)

            if 'HOST' in self.database_config and self.database_config['HOST']:
                self.args.append('--host=%(HOST)s' % self.database_config)

            if 'PORT' in self.database_config and self.database_config['PORT']:
                self.args.append('--port=%(PORT)d' % self.database_config)

            self.args.append('--dbname=%(NAME)s' % self.database_config)

        self.args.append('--table=%s.%s' % (schema_name, table_name))
