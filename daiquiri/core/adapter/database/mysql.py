import logging
import re

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
        'text': {
            'datatype': 'char',
            'arraysize': True
        },
        'tinyint': {
            'datatype': 'boolean',
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

    COLUMNTYPES = {
        'char': 'text',
        'boolean': 'boolean',
        'short': 'smallint',
        'int': 'int',
        'long': 'bigint',
        'float': 'float',
        'double': 'double'
    }

    search_stmt_template = '%s LIKE %%s'
    search_arg_template = '%%%s%%'

    def fetch_pid(self):
        return self.connection().connection.thread_id()

    def escape_identifier(self, identifier):
        # escape backticks within the identifier and backtick the string
        return '`{}`'.format(identifier.replace('`', '``'))

    def escape_string(self, string):
        return f"'{string}'"

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
            return 'CREATE TABLE {schema}.{table} ENGINE=MyISAM ( {query} ) LIMIT {max_records};'.format(**params)
        else:
            return 'CREATE TABLE {schema}.{table} ENGINE=MyISAM ( {query} );'.format(**params)

    def build_sync_query(self, query, timeout, max_records):
        # construct the actual query
        params = {
            'query': query,
            'timeout': timeout,
            'max_records': max_records
        }

        if max_records is not None:
            return '{query} LIMIT {max_records};'.format(**params)
        else:
            return '{query};'.format(**params)

    def abort_query(self, pid):
        sql = 'KILL %(pid)i' % {'pid': pid}
        self.execute(sql)

    def fetch_size(self, schema_name, table_name):
        sql = 'SELECT data_length + index_length AS size FROM `information_schema`.`tables` WHERE `table_schema` = %s AND table_name = %s;'  # noqa: E501
        size = self.fetchone(sql, (schema_name, table_name))[0]

        # log values and return
        logger.debug('size = %d', size)
        return size

    def fetch_nrows(self, schema_name, table_name):
        sql = 'SELECT table_rows as nrows FROM `information_schema`.`tables` WHERE `table_schema` = %s AND table_name = %s;'  # noqa: E501
        nrows = self.fetchone(sql, (schema_name, table_name))[0]

        # log values and return
        logger.debug('size = %d', nrows)
        return nrows

    def fetch_tables(self, schema_name):
        # escape input
        escaped_schema_name = self.escape_identifier(schema_name)

        # prepare sql string
        sql = f'SHOW FULL TABLES FROM {escaped_schema_name}'

        # execute query
        try:
            rows = self.fetchall(sql)
        except OperationalError as e:
            logger.error('Could not fetch from %s (%s)', schema_name, e)
            return []
        else:
            return [{
                'name': row[0],
                'type': 'view' if row[1] == 'VIEW' else 'table'
            } for row in rows]

    def fetch_table(self, schema_name, table_name):
        # prepare sql string
        sql = f'SHOW FULL TABLES FROM {self.escape_identifier(schema_name)} LIKE {self.escape_string(table_name)}'

        # execute query
        try:
            row = self.fetchone(sql)
        except OperationalError as e:
            logger.error('Could not fetch %s.%s (%s)', schema_name, table_name, e)
            return {}
        else:
            if row is None:
                logger.info('Could not fetch %s.%s. Check if table and schema exist.', schema_name, table_name)
                return {}
            else:
                return {
                    'name': row[0],
                    'type': 'view' if row[1] == 'VIEW' else 'table'
                }

    def fetch_columns(self, schema_name, table_name):
        # prepare sql string
        sql = f'SHOW FULL COLUMNS FROM {self.escape_identifier(schema_name)}.{self.escape_identifier(table_name)};'

        # execute query
        try:
            rows = self.fetchall(sql)
        except ProgrammingError as e:
            logger.error('Could not fetch columns from %s.%s (%s)', schema_name, table_name, e)
            return []
        else:
            columns = []
            for row in rows:
                datatype, arraysize = self._convert_datatype(row[1])

                columns.append({
                    'name': row[0],
                    'datatype': datatype,
                    'arraysize': arraysize,
                    'indexed': bool(row[4])
                })

            return columns

    def fetch_column(self, schema_name, table_name, column_name):
        # prepare sql string
        sql = f'SHOW FULL COLUMNS FROM {self.escape_identifier(schema_name)}.{self.escape_identifier(table_name)} WHERE `Field` = {self.escape_string(column_name)}'  # noqa: E501

        # execute query
        try:
            row = self.fetchone(sql)
        except ProgrammingError as e:
            logger.error('Could not fetch %s.%s.%s (%s)', schema_name, table_name, column_name, e)
            return {}
        else:
            if row is None:
                logger.info(f'Could not fetch {schema_name}.{table_name}.{column_name}. Check if column, table and schema exist.')
                return {}
            else:
                return {
                    'name': row[0],
                    'datatype': row[1],
                    'indexed': bool(row[4])
                }

    def fetch_column_names(self, schema_name, table_name):
        # prepare sql string
        sql = f'SHOW COLUMNS FROM {self.escape_identifier(schema_name)}.{self.escape_identifier(table_name)}'
        return [column[0] for column in self.fetchall(sql)]

    def rename_table(self, schema_name, table_name, new_table_name):
        sql = 'RENAME TABLE {schema}.{table} to {schema}.{new_table};'.format(
            schema=self.escape_identifier(schema_name),
            table=self.escape_identifier(table_name),
            new_table=self.escape_identifier(new_table_name),
        )

        self.execute(sql)

    def _convert_datatype(self, datatype_string):
        result = re.match(r'([a-z]+)\(*(\d*)\)*', datatype_string)

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
