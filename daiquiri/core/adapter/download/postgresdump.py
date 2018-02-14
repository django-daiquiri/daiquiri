import logging
import re


from .base import DownloadAdapter

logger = logging.getLogger(__name__)

class PostgreSQLdumpAdapter(DownloadAdapter):

    insert_pattern = re.compile('^INSERT INTO .*? VALUES \((.*?)\);')

    FORMATS = {
        'char': 'c',
        'unsignedByte': 'B',
        'short': 'h',
        'integer': 'i',
        'long': 'q',
        'float': 'f',
        'double': 'd'
    }

    NULL_VALUES = {
        'char': '',
        'unsignedByte': 255,
        'short': 32767,
        'integer': 2147483647,
        'long': 9223372036854775807,
        'float': float('nan'),
        'double': float('nan')
    }

    def __init__(self, database_key, database_config):
        # TODO: argument string to pass
        # command line for pg_dump:
        # pg_dump --dbname=postgresql://user:password@host:port/database --table=schema.table 
        # '--dbname=postgresql://%(USER)s:%(PASSWORD)s@%(HOST)s:%(PORT)s/%(NAME)s' % database_config

        self.args = ['pg_dump', '-a', '--inserts']
        dbname_arg = '--dbname=postgresql://'

        if 'USER' in database_config and database_config['USER']:
                dbname_arg += '%(USER)s' % database_config

        if 'PASSWORD' in database_config and database_config['PASSWORD']:
            dbname_arg +=':%(PASSWORD)s' % database_config
        
        if 'HOST' in database_config and database_config['HOST']:
            dbname_arg +='@%(HOST)s' % database_config

        if 'PORT' in database_config and database_config['PORT']:
            dbname_arg +=':%(PORT)s' % database_config
        
        if 'NAME' in database_config and database_config['NAME']:
            dbname_arg +='/%(NAME)s' % database_config

        self.args.append(dbname_arg)
        logger.debug('download init: %s' % (self.args))

    def _set_args(self, schema_name, table_name):
        # append --table=schema.table
        self.args.append('--table=%s.%s' % (schema_name, table_name))
        logger.debug('download set args: %s' % (self.args))
        return self.args