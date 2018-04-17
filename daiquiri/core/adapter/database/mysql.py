import logging
import re
import warnings

from django.db import OperationalError, ProgrammingError

from .base import BaseDatabaseAdapter

logger = logging.getLogger(__name__)


class MySQLAdapter(BaseDatabaseAdapter):

    DATATYPES = {
        'char': {
            'datatype': 'char',
            'arraysize': True
        },
        'varchar': {
            'datatype': 'char',
            'arraysize': True
        },
        'tinyint': {
            'datatype': 'unsignedByte',
            'arraysize': False
        },
        'smallint': {
            'datatype': 'short',
            'arraysize': False
        },
        'int': {
            'datatype': 'int',
            'arraysize': False
        },
        'bigint': {
            'datatype': 'long',
            'arraysize': False
        },
        'float': {
            'datatype': 'float',
            'arraysize': False
        },
        'double': {
            'datatype': 'double',
            'arraysize': False
        },
        'timestamp': {
            'datatype': 'timestamp',
            'arraysize': False
        }
    }

    search_stmt_template = '%s LIKE %%s'
    search_arg_template = '%%%s%%'

    def fetch_pid(self):
        return self.connection().connection.thread_id()

    def escape_identifier(self, identifier):
        # escape backticks whithin the identifier and backtick the string
        return '`%s`' % identifier.replace('`', '``')

    def escape_string(self, string):
        return "'%s'" % string

    def build_query(self, schema_name, table_name, query, timeout, max_records):
        # construct the actual query
        params = {
            'schema': self.escape_identifier(schema_name),
            'table': self.escape_identifier(table_name),
            'query': query,
            'timeout': timeout,
            'max_records': max_records
        }

        if max_records is not None:
            return 'CREATE TABLE %(schema)s.%(table)s ENGINE=MyISAM ( %(query)s ) LIMIT %(max_records)s;' % params
        else:
            return 'CREATE TABLE %(schema)s.%(table)s ENGINE=MyISAM ( %(query)s );' % params

    def submit_query(self, sql):
        self.execute(sql)

    def abort_query(self, pid):
        sql = 'KILL %(pid)i' % {'pid': pid}
        self.execute(sql)

    def fetch_size(self, schema_name, table_name):
        sql = 'SELECT data_length + index_length AS size FROM `information_schema`.`tables` WHERE `table_schema` = %s AND table_name = %s;'
        size = self.fetchone(sql, (schema_name, table_name))[0]

        # log values and return
        logger.debug('size = %d', size)
        return size

    def fetch_nrows(self, schema_name, table_name):
        sql = 'SELECT table_rows as nrows FROM `information_schema`.`tables` WHERE `table_schema` = %s AND table_name = %s;'
        nrows = self.fetchone(sql, (schema_name, table_name))[0]

        # log values and return
        logger.debug('size = %d', nrows)
        return nrows

    def count_rows(self, schema_name, table_name, column_names=None, search=None, filters=None):
        # if no column names are provided get all column_names from the table
        if not column_names:
            column_names = self.fetch_column_names(schema_name, table_name)

        # create a list of escaped columns
        escaped_column_names = [self.escape_identifier(column_name) for column_name in column_names]

        # prepare sql string
        sql = 'SELECT COUNT(*) FROM %(schema)s.%(table)s' % {
            'schema': self.escape_identifier(schema_name),
            'table': self.escape_identifier(table_name)
        }
        sql_args = []

        # process filtering
        sql, sql_args = self._process_filtering(sql, sql_args, search, filters, escaped_column_names)

        return self.fetchone(sql, args=sql_args)[0]

    def fetch_row(self, schema_name, table_name, column_names=None, search=None, filters=None):

        # if no column names are provided get all column_names from the table
        if not column_names:
            column_names = self.fetch_column_names(schema_name, table_name)

        # create a list of escaped columns
        escaped_column_names = [self.escape_identifier(column_name) for column_name in column_names]

        # prepare sql string
        sql = 'SELECT %(columns)s FROM %(schema)s.%(table)s' % {
            'schema': self.escape_identifier(schema_name),
            'table': self.escape_identifier(table_name),
            'columns': ', '.join(escaped_column_names)
        }
        sql_args = []

        # process filtering
        sql, sql_args = self._process_filtering(sql, sql_args, search, filters, escaped_column_names)

        return self.fetchone(sql, args=sql_args)

    def fetch_dict(self, schema_name, table_name, column_names=None, search=None, filters=None):

        # if no column names are provided get all column_names from the table
        if not column_names:
            column_names = self.fetch_column_names(schema_name, table_name)

        row = self.fetch_row(schema_name, table_name, column_names, search, filters)

        if row:
            return {
                column_name: value for column_name, value in zip(column_names, row)
            }
        else:
            return {}

    def fetch_rows(self, schema_name, table_name, column_names=None, ordering=None, page=1, page_size=10, search=None, filters=None):

        # if no column names are provided get all column_names from the table
        if not column_names:
            column_names = self.fetch_column_names(schema_name, table_name)

        # create a list of escaped columns
        escaped_column_names = [self.escape_identifier(column_name) for column_name in column_names]

        # init sql string and sql_args list
        sql = 'SELECT %(columns)s FROM %(schema)s.%(table)s' % {
            'schema': self.escape_identifier(schema_name),
            'table': self.escape_identifier(table_name),
            'columns': ', '.join(escaped_column_names)
        }
        sql_args = []

        # process filtering
        sql, sql_args = self._process_filtering(sql, sql_args, search, filters, escaped_column_names)

        # process ordering
        sql = self._process_ordering(sql, ordering, escaped_column_names)

        # process page and page_size
        if page_size > 0:
            sql += ' LIMIT %(limit)s OFFSET %(offset)s' % {
                'limit': page_size,
                'offset': (int(page) - 1) * int(page_size)
            }

        return self.fetchall(sql, args=sql_args)

    def create_user_schema_if_not_exists(self, schema_name):
        # escape input
        escaped_schema_name = self.escape_identifier(schema_name)

        # prepare sql string
        sql = 'CREATE DATABASE IF NOT EXISTS %(schema)s' % {
            'schema': escaped_schema_name
        }

        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            self.execute(sql)

    def fetch_tables(self, schema_name):
        # escape input
        escaped_schema_name = self.escape_identifier(schema_name)

        # prepare sql string
        sql = 'SHOW FULL TABLES FROM %(schema)s' % {
            'schema': escaped_schema_name
        }

        # execute query
        try:
            rows = self.fetchall(sql)
        except OperationalError as e:
            logger.error('Could not fetch from %s (%s)' % (schema_name, e))
            return []
        else:
            return [{
                'name': row[0],
                'type': 'view' if row[1] == 'VIEW' else 'table'
            } for row in rows]

    def fetch_table(self, schema_name, table_name):
        # prepare sql string
        sql = 'SHOW FULL TABLES FROM %(schema)s LIKE %(table)s' % {
            'schema': self.escape_identifier(schema_name),
            'table': self.escape_string(table_name)
        }

        # execute query
        try:
            row = self.fetchone(sql)
        except OperationalError as e:
            logger.error('Could not fetch %s.%s (%s)' % (schema_name, table_name, e))
            return {}
        else:
            return {
                'name': row[0],
                'type': 'view' if row[1] == 'VIEW' else 'table'
            }

    def rename_table(self, schema_name, table_name, new_table_name):
        sql = 'RENAME TABLE %(schema)s.%(table)s to %(schema)s.%(new_table)s;' % {
            'schema': self.escape_identifier(schema_name),
            'table': self.escape_identifier(table_name),
            'new_table': self.escape_identifier(new_table_name)
        }

        self.execute(sql)

    def drop_table(self, schema_name, table_name):
        sql = 'DROP TABLE IF EXISTS %(schema)s.%(table)s;' % {
            'schema': self.escape_identifier(schema_name),
            'table': self.escape_identifier(table_name)
        }

        self.execute(sql)

    def fetch_columns(self, schema_name, table_name):
        # prepare sql string
        sql = 'SHOW FULL COLUMNS FROM %(schema)s.%(table)s;' % {
            'schema': self.escape_identifier(schema_name),
            'table': self.escape_identifier(table_name)
        }

        # execute query
        try:
            rows = self.fetchall(sql)
        except ProgrammingError as e:
            logger.error('Could not fetch columns from %s.%s (%s)' % (schema_name, table_name, e))
            return []
        else:
            columns = []
            for row in rows:
                datatype, arraysize = self.convert_datatype(row[1])

                columns.append({
                    'name': row[0],
                    'datatype': datatype,
                    'arraysize': arraysize,
                    'indexed': bool(row[4])
                })

            return columns

    def fetch_column(self, schema_name, table_name, column_name):
        # prepare sql string
        sql = 'SHOW FULL COLUMNS FROM %(schema)s.%(table)s WHERE `Field` = %(column)s' % {
            'schema': self.escape_identifier(schema_name),
            'table': self.escape_identifier(table_name),
            'column': self.escape_string(column_name)
        }

        # execute query
        try:
            row = self.fetchone(sql)
        except ProgrammingError as e:
            logger.error('Could not fetch %s.%s.%s (%s)' % (schema_name, table_name, column_name, e))
            return {}
        else:
            return {
                'name': row[0],
                'datatype': row[1],
                'indexed': bool(row[4])
            }

    def fetch_column_names(self, schema_name, table_name):
        # prepare sql string
        sql = 'SHOW COLUMNS FROM %(schema)s.%(table)s' % {
            'schema': self.escape_identifier(schema_name),
            'table': self.escape_identifier(table_name),
        }
        return [column[0] for column in self.fetchall(sql)]

    def convert_datatype(self, datatype_string):
        result = re.match('([a-z]+)\(*(\d*)\)*', datatype_string)

        if result:
            native_datatype = result.group(1)

            try:
                native_arraysize = int(result.group(2))
            except ValueError:
                native_arraysize = None

            if native_datatype in self.DATATYPES:
                datatype = self.DATATYPES[native_datatype]['datatype']

                if self.DATATYPES[native_datatype]['arraysize']:
                    arraysize = native_arraysize
                else:
                    arraysize = None

                return datatype, arraysize
            else:
                return native_datatype, native_arraysize
        else:
            return datatype_string, None
