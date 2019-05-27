import logging

from django.db import OperationalError, ProgrammingError

from .base import BaseDatabaseAdapter

logger = logging.getLogger(__name__)


class PostgreSQLAdapter(BaseDatabaseAdapter):

    DATATYPES = {
        'character': {
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
        'boolean': {
            'datatype': 'boolean',
            'arraysize': False
        },
        'smallint': {
            'datatype': 'short',
            'arraysize': False
        },
        'integer': {
            'datatype': 'int',
            'arraysize': False
        },
        'bigint': {
            'datatype': 'long',
            'arraysize': False
        },
        'real': {
            'datatype': 'float',
            'arraysize': False
        },
        'double precision': {
            'datatype': 'double',
            'arraysize': False
        }
    }

    COLUMNTYPES = {
        'char': 'text',
        'boolean': 'boolean',
        'short': 'smallint',
        'int': 'integer',
        'long': 'bigint',
        'float': 'real',
        'double': 'double precision'
    }

    search_stmt_template = '%s::text LIKE %%s'
    search_arg_template = '%%%s%%'

    def fetch_pid(self):
        return self.connection().connection.get_backend_pid()

    def escape_identifier(self, identifier):
        # escape quotes whithin the identifier and quote the string
        return '"%s"' % identifier.replace('"', '""')

    def escape_string(self, string):
        return "'%s'" % string

    def build_query(self, schema_name, table_name, query, timeout, max_records):
        # construct the actual query
        params = {
            'schema': self.escape_identifier(schema_name),
            'table': self.escape_identifier(table_name),
            'query': query,
            'timeout': int(timeout * 1000),
            'max_records': max_records
        }

        if max_records is not None:
            return 'SET SESSION statement_timeout TO %(timeout)s; COMMIT; CREATE TABLE %(schema)s.%(table)s AS %(query)s LIMIT %(max_records)s;' % params
        else:
            return 'SET SESSION statement_timeout TO %(timeout)s; COMMIT; CREATE TABLE %(schema)s.%(table)s AS %(query)s;' % params

    def build_sync_query(self, query, timeout, max_records):
        # construct the actual query
        params = {
            'query': query,
            'timeout': int(timeout * 1000),
            'max_records': max_records
        }

        if max_records is not None:
            return 'SET SESSION statement_timeout TO %(timeout)s; COMMIT; %(query)s LIMIT %(max_records)s;' % params
        else:
            return 'SET SESSION statement_timeout TO %(timeout)s; COMMIT; %(query)s;' % params

    def abort_query(self, pid):
        sql = 'select pg_cancel_backend(%(pid)i)' % {'pid': pid}
        self.execute(sql)

    def fetch_size(self, schema_name, table_name):
        # fetch the size of the table using pg_total_relation_size
        sql = 'SELECT pg_total_relation_size(\'%(schema)s.%(table)s\')' % {
            'schema': self.escape_identifier(schema_name),
            'table': self.escape_identifier(table_name)
        }
        size = self.fetchone(sql)[0]

        # log values and return
        logger.debug('size = %d', size)
        return size

    def fetch_nrows(self, schema_name, table_name):
        # fetch the size of the table using pg_total_relation_size
        sql = 'SELECT reltuples::BIGINT FROM pg_class WHERE oid = \'%(schema)s.%(table)s\'::regclass;' % {
            'schema': self.escape_identifier(schema_name),
            'table': self.escape_identifier(table_name)
        }
        nrows = self.fetchone(sql)[0]

        # log values and return
        logger.debug('nrows = %d', nrows)
        return nrows

    def fetch_tables(self, schema_name):
        # escape input
        escaped_schema_name = self.escape_string(schema_name)

        # prepare sql string
        sql = 'SELECT table_name, table_type FROM information_schema.tables where table_schema = %(schema)s' % {
            'schema': escaped_schema_name
        }

        # log sql string
        logger.debug('sql = "%s"', sql)

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
        sql = 'SELECT table_name, table_type FROM information_schema.tables where table_schema = %(schema)s AND table_name = %(table)s' % {
            'schema': self.escape_string(schema_name),
            'table': self.escape_string(table_name)
        }

        # log sql string
        logger.debug('sql = "%s"', sql)

        # execute query
        try:
            row = self.fetchone(sql)
        except OperationalError as e:
            logger.error('Could not fetch %s.%s (%s)', schema_name, table_name, e)
            return {}
        else:
            if row is None:
                logger.info('Could not fetch %s.%s. Check if table and schema exist.', schema_name, table_name)
                return []
            else:
                return {
                    'name': row[0],
                    'type': 'view' if row[1] == 'VIEW' else 'table'
                }

    def fetch_columns(self, schema_name, table_name):
        logger.debug('fetch_columns %s %s' % (schema_name, table_name))

        # prepare sql string
        sql = 'SELECT column_name, data_type, udt_name, character_maximum_length, ordinal_position FROM information_schema.columns WHERE table_schema = %(schema)s AND table_name = %(table)s' % {
            'schema': self.escape_string(schema_name),
            'table': self.escape_string(table_name)
        }

        # log sql string
        logger.debug('sql = "%s"', sql)

        # execute query
        try:
            rows = self.fetchall(sql)
        except ProgrammingError as e:
            logger.error('Could not fetch columns from %s.%s (%s)', schema_name, table_name, e)
            return []
        else:
            columns = []
            for row in rows:
                columns.append(self._parse_column(row))

            # check if indexed
            sql = 'SELECT indexdef FROM pg_indexes WHERE schemaname = %(schema)s AND tablename = %(table)s' % {
                'schema': self.escape_string(schema_name),
                'table': self.escape_string(table_name)
            }

            # log sql string
            logger.debug('sql = "%s"', sql)

            try:
                rows = self.fetchall(sql)
            except OperationalError as e:
                logger.error('Could not fetch indexes of %s.%s (%s)', schema_name, table_name, e)
                return columns
            else:
                for column in columns:
                    columnname = '(' + column['name'] + ')'
                    if str(rows).find(columnname) > -1:
                        column['indexed'] = True
            return columns

    def fetch_column(self, schema_name, table_name, column_name):
        # prepare sql string
        sql = 'SELECT column_name, data_type, udt_name, character_maximum_length, ordinal_position FROM information_schema.columns WHERE table_schema = %(schema)s AND table_name = %(table)s AND column_name = %(column)s' % {
            'schema': self.escape_string(schema_name),
            'table': self.escape_string(table_name),
            'column': self.escape_string(column_name)
        }

        # log sql string
        logger.debug('sql = "%s"', sql)

        # execute query
        try:
            row = self.fetchone(sql)
        except ProgrammingError as e:
            logger.error('Could not fetch %s.%s.%s (%s)', schema_name, table_name, column_name, e)
            return []
        else:
            if row is None:
                logger.info('Could not fetch %s.%s.%s. Check if the schema exists.', schema_name, table_name, column_name)
                return []
            else:
                column = self._parse_column(row)

            # check if indexed
            sql = 'SELECT indexdef FROM pg_indexes WHERE schemaname = %(schema)s AND tablename = %(table)s' % {
                'schema': self.escape_string(schema_name),
                'table': self.escape_string(table_name)
            }

            # log sql string
            logger.debug('sql = "%s"', sql)

            try:
                rows = self.fetchall(sql)
            except OperationalError as e:
                logger.error('Could not fetch indexes of %s.%s.%s (%s)', schema_name, table_name, column_name, e)
                return column
            else:
                columnname = '(\'' + column['name'] + '\')'
                if str(rows).find(columnname) > -1:
                    column['indexed'] = True
            return column

    def fetch_column_names(self, schema_name, table_name):
        logger.debug('schema_name = "%s"', schema_name)
        logger.debug('table_name = "%s"', table_name)

        # prepare sql string
        sql = 'SELECT column_name FROM information_schema.columns where table_schema = %(schema)s AND table_name = %(table)s' % {
            'schema': self.escape_string(schema_name),
            'table': self.escape_string(table_name)
        }

        # log values and return
        logger.debug('sql = "%s"', sql)
        return [column[0] for column in self.fetchall(sql)]

    def rename_table(self, schema_name, table_name, new_table_name):
        sql = 'ALTER TABLE %(schema)s.%(table)s RENAME TO %(new_table)s;' % {
            'schema': self.escape_identifier(schema_name),
            'table': self.escape_identifier(table_name),
            'new_table': self.escape_identifier(new_table_name)
        }

        # log sql string and execute
        logger.debug('sql = "%s"', sql)
        self.execute(sql)

    def _parse_column(self, row):
        column_name, data_type, udt_name, character_maximum_length, ordinal_position = row

        column = {
            'name': column_name
        }

        if data_type.lower() in self.DATATYPES:
            datatype = self.DATATYPES[data_type.lower()]
        elif udt_name.lower() in self.DATATYPES:
            datatype = self.DATATYPES[udt_name.lower()]
        else:
            datatype = None

        if datatype:
            column['datatype'] = datatype['datatype']

            if datatype['arraysize']:
                column['arraysize'] = character_maximum_length
            else:
                column['arraysize'] = None
        else:
            column['datatype'] = 'char'
            column['arraysize'] = 32

        column['order'] = ordinal_position

        # log values and return
        logger.debug('row = %s', row)
        logger.debug('column = %s', column)
        return column
