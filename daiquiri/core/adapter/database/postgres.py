import logging

from django.conf import settings
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
        },
        'spoint':{
            'datatype': 'char',
            'arraysize': True
        },
        '_int2': {
            'datatype': 'short',
            'arraysize': '*'
        },
        '_int4': {
            'datatype': 'int',
            'arraysize': '*'
        },
        '_int8': {
            'datatype': 'long',
            'arraysize': '*'
        },
        '_float4': {
            'datatype': 'float',
            'arraysize': '*'
        },
        '_float8': {
            'datatype': 'double',
            'arraysize': '*'
        },
        '_bool': {
            'datatype': 'boolean',
            'arraysize': '*'
        }
    }

    COLUMNTYPES = {
        'char': 'text',
        'unicodeChar': 'text',
        'boolean': 'boolean',
        'bit': 'boolean',
        # 'unsignedByte': ???, not supported by Postgres... could be solved with pguint extension
        'short': 'smallint',
        'int': 'integer',
        'long': 'bigint',
        'float': 'real',
        'double': 'double precision',
        #'floatComplex': ???, not supported by Postgres
        #'doubleComplex': ???, not supported by Postgres
        'spoint': 'spoint',
    }

    search_stmt_template = '%s::text LIKE %%s'
    search_arg_template = '%%%s%%'

    def fetch_pid(self):
        return self.connection().connection.info.backend_pid

    def escape_identifier(self, identifier):
        # escape quotes within the identifier and quote the string
        return '"{}"'.format(identifier.replace('"', '""'))

    def escape_string(self, string):
        return f"'{string}'"

    def build_query(self, schema_name, table_name, query, timeout, max_records):
        # construct the actual query
        params = {
            'schema': self.escape_identifier(schema_name),
            'table': self.escape_identifier(table_name),
            'query': query,
            'timeout': int(timeout * 1000),
            'max_records': max_records,
            'tablespace': settings.USER_TABLESPACE,
        }

        query = 'SET SESSION statement_timeout TO %(timeout)s; COMMIT; CREATE TABLE %(schema)s.%(table)s'

        if params['tablespace'] is not None:
            query = query + ' TABLESPACE %(tablespace)s AS %(query)s'
        else:
            query = query + ' AS %(query)s'

        if params['max_records'] is not None:
            query = query + ' LIMIT %(max_records)s'

        query = query + ';'

        return query % params


    def build_sync_query(self, query, timeout, max_records):
        # construct the actual query
        params = {
            'query': query,
            'timeout': int(timeout * 1000),
            'max_records': max_records
        }

        if max_records is not None:
            return 'SET SESSION statement_timeout TO {timeout}; COMMIT; {query} LIMIT {max_records};'.format(**params)
        else:
            return 'SET SESSION statement_timeout TO {timeout}; COMMIT; {query};'.format(**params)

    def abort_query(self, pid):
        sql = 'select pg_cancel_backend(%(pid)i)' % {'pid': pid}
        self.execute(sql)

    def fetch_size(self, schema_name, table_name):
        # fetch the size of the table using pg_total_relation_size
        sql = f'SELECT pg_total_relation_size(\'{self.escape_identifier(schema_name)}.{self.escape_identifier(table_name)}\')'  # noqa: E501
        size = self.fetchone(sql)[0]

        # log values and return
        logger.debug('size = %d', size)
        return size

    def fetch_nrows(self, schema_name, table_name):
        # fetch the size of the table using pg_total_relation_size
        sql = f'SELECT reltuples::BIGINT FROM pg_class WHERE oid = \'{self.escape_identifier(schema_name)}.{self.escape_identifier(table_name)}\'::regclass;'  # noqa: E501
        nrows = self.fetchone(sql)[0]

        # log values and return
        logger.debug('nrows = %d', nrows)
        return nrows

    def fetch_tables(self, schema_name):
        # escape input
        escaped_schema_name = self.escape_string(schema_name)

        # prepare sql string
        sql = f'SELECT table_name, table_type FROM information_schema.tables where table_schema = {escaped_schema_name}'

        # log sql string
        logger.debug('sql = "%s"', sql)

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
        sql = f'SELECT table_name, table_type FROM information_schema.tables where table_schema = {self.escape_string(schema_name)} AND table_name = {self.escape_string(table_name)}'  # noqa: E501

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
                return {}
            else:
                return {
                    'name': row[0],
                    'type': 'view' if row[1] == 'VIEW' else 'table'
                }

    def fetch_columns(self, schema_name, table_name):
        logger.debug('fetch_columns %s %s', schema_name, table_name)

        # prepare sql string
        sql = f'SELECT column_name, data_type, udt_name, character_maximum_length, ordinal_position FROM information_schema.columns WHERE table_schema = {self.escape_string(schema_name)} AND table_name = {self.escape_string(table_name)}'  # noqa: E501

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
            sql = f'SELECT indexdef FROM pg_indexes WHERE schemaname = {self.escape_string(schema_name)} AND tablename = {self.escape_string(table_name)}'  # noqa: E501

            # log sql string
            logger.debug('sql = "%s"', sql)

            try:
                rows = self.fetchall(sql)
            except OperationalError as e:
                logger.error('Could not fetch indexes of %s.%s (%s)', schema_name, table_name, e)
                return columns
            else:
                for column in columns:
                    columnname = '({})'.format(column['name'])
                    if str(rows).find(columnname) > -1:
                        column['indexed'] = True
            return columns

    def fetch_column(self, schema_name, table_name, column_name):
        # prepare sql string
        sql = f'SELECT column_name, data_type, udt_name, character_maximum_length, ordinal_position FROM information_schema.columns WHERE table_schema = {self.escape_string(schema_name)} AND table_name = {self.escape_string(table_name)} AND column_name = {self.escape_string(column_name)}'  # noqa: E501

        # log sql string
        logger.debug('sql = "%s"', sql)

        # execute query
        try:
            row = self.fetchone(sql)
        except ProgrammingError as e:
            logger.error('Could not fetch %s.%s.%s (%s)', schema_name, table_name, column_name, e)
            return {}
        else:
            if row is None:
                logger.info('Could not fetch %s.%s.%s. Check if the schema exists.', schema_name, table_name, column_name)  # noqa: E501
                return {}
            else:
                column = self._parse_column(row)

            # check if indexed
            sql = f'SELECT indexdef FROM pg_indexes WHERE schemaname = {self.escape_string(schema_name)} AND tablename = {self.escape_string(table_name)}'  # noqa: E501

            # log sql string
            logger.debug('sql = "%s"', sql)

            try:
                rows = self.fetchall(sql)
            except OperationalError as e:
                logger.error('Could not fetch indexes of %s.%s.%s (%s)', schema_name, table_name, column_name, e)
                return column
            else:
                columnname = '({})'.format(column['name'])
                if str(rows).find(columnname) > -1:
                    column['indexed'] = True

            return column

    def fetch_column_names(self, schema_name, table_name):
        logger.debug('schema_name = "%s"', schema_name)
        logger.debug('table_name = "%s"', table_name)

        # prepare sql string
        sql = f'SELECT column_name FROM information_schema.columns where table_schema = {self.escape_string(schema_name)} AND table_name = {self.escape_string(table_name)}'  # noqa: E501

        # log values and return
        logger.debug('sql = "%s"', sql)
        return [column[0] for column in self.fetchall(sql)]

    def rename_table(self, schema_name, table_name, new_table_name):
        sql = f'ALTER TABLE {self.escape_identifier(schema_name)}.{self.escape_identifier(table_name)} RENAME TO {self.escape_identifier(new_table_name)};'  # noqa: E501

        # log sql string and execute
        logger.debug('sql = "%s"', sql)
        self.execute(sql)

    def _parse_column(self, row):
        column_name, data_type, udt_name, character_maximum_length, ordinal_position = row

        column = {
            'name': column_name
        }

        if udt_name.lower() in self.DATATYPES: # universal types: int2, int4, int8, _float8, ...
            datatype = self.DATATYPES[udt_name.lower()]

        elif data_type.lower() in self.DATATYPES: # postgres types: smallint, bigint, ARRAY, ...
            datatype = self.DATATYPES[data_type.lower()]

        else:
            datatype = None

        if datatype:
            if '_' in udt_name.lower(): # ARRAY
                column['datatype'] = datatype['datatype'] # the _ is still needed, will be removed by the serializer.
                column['arraysize'] = '*'

            else:
                column['datatype'] = datatype['datatype']

                if datatype['arraysize'] is True:
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
