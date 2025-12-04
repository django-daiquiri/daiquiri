import logging

from django.conf import settings
from django.db import OperationalError, ProgrammingError

from .base import BaseDatabaseAdapter

logger = logging.getLogger(__name__)


class PostgreSQLAdapter(BaseDatabaseAdapter):
    DATATYPES = {
        'character': {'datatype': 'char', 'arraysize': True},
        'varchar': {'datatype': 'char', 'arraysize': True},
        'text': {'datatype': 'char', 'arraysize': False},
        'boolean': {'datatype': 'boolean', 'arraysize': False},
        'smallint': {'datatype': 'short', 'arraysize': False},
        'integer': {'datatype': 'int', 'arraysize': False},
        'bigint': {'datatype': 'long', 'arraysize': False},
        'real': {'datatype': 'float', 'arraysize': False},
        'double precision': {'datatype': 'double', 'arraysize': False},
        'spoint': {'datatype': 'char', 'arraysize': True},
        '_int2': {'datatype': 'short', 'arraysize': '*'},
        '_int4': {'datatype': 'int', 'arraysize': '*'},
        '_int8': {'datatype': 'long', 'arraysize': '*'},
        '_float4': {'datatype': 'float', 'arraysize': '*'},
        '_float8': {'datatype': 'double', 'arraysize': '*'},
        '_bool': {'datatype': 'boolean', 'arraysize': '*'},
        '_varchar': {'datatype': 'char', 'arraysize': '*'},
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

    def fetchall_sync(self, sql):
        conn = self.connection()
        with conn.cursor() as cursor:
            cursor.execute(sql)

            while cursor.description is None and cursor.nextset():
                pass

            database_columns = cursor.description

            rows = cursor.fetchall()
            columns = self.fetch_columns_sync(database_columns)

            return columns, rows

    def build_query(self, schema_name, table_name, query, timeout, max_records):
        # max_records is now handled by the method trim_table_rows
        actual_query = (
            f'SET SESSION statement_timeout TO {int(timeout * 1000)};'
            + 'COMMIT;'
            + f'CREATE TABLE {self.escape_identifier(schema_name)}'
            + f'.{self.escape_identifier(table_name)}'
        )

        if settings.USER_TABLESPACE is not None:
            actual_query += f' TABLESPACE {settings.USER_TABLESPACE}'

        actual_query += f' AS {query};'

        return actual_query

    def build_sync_query(self, query, timeout, max_records):
        # max_records is now handled by the method trim_table_rows
        return f'SET SESSION statement_timeout TO {int(timeout * 1000)}; COMMIT; {query};'

    def abort_query(self, pid: int):
        sql = f'SELECT pg_cancel_backend({pid})'
        self.execute(sql)

    def fetch_size(self, schema_name, table_name):
        sql = (
            'SELECT pg_total_relation_size('
            + f"'{self.escape_identifier(schema_name)}.{self.escape_identifier(table_name)}')"
        )
        size = self.fetchone(sql)[0]

        logger.debug('size = %d', size)
        return size

    def fetch_nrows(self, schema_name, table_name):
        # fetch the size of the table using pg_total_relation_size
        sql = (
            'SELECT reltuples::BIGINT FROM pg_class '
            + f"WHERE oid = '{self.escape_identifier(schema_name)}.{self.escape_identifier(table_name)}'::regclass;"  # noqa: E501
        )
        nrows = self.fetchone(sql)[0]

        # log values and return
        logger.debug('nrows = %d', nrows)
        return nrows

    def fetch_tables(self, schema_name):
        escaped_schema_name = self.escape_string(schema_name)

        sql = (
            'SELECT table_name, table_type FROM information_schema.tables '
            + f'WHERE table_schema = {escaped_schema_name}'
        )

        logger.debug('sql = "%s"', sql)

        try:
            rows = self.fetchall(sql)
        except OperationalError as e:
            logger.error('Could not fetch from %s (%s)', schema_name, e)
            return []
        else:
            return [
                {'name': row[0], 'type': 'view' if row[1] == 'VIEW' else 'table'} for row in rows
            ]

    def fetch_table(self, schema_name, table_name):
        sql = (
            'SELECT table_name, table_type FROM information_schema.tables '
            + f'WHERE table_schema = {self.escape_string(schema_name)} '
            + f'AND table_name = {self.escape_string(table_name)}'
        )

        logger.debug('sql = "%s"', sql)

        try:
            row = self.fetchone(sql)
        except OperationalError as e:
            logger.error('Could not fetch %s.%s (%s)', schema_name, table_name, e)
            return {}
        else:
            if row is None:
                logger.info(
                    'Could not fetch %s.%s. Check if table and schema exist.',
                    schema_name,
                    table_name,
                )
                return {}
            else:
                return {'name': row[0], 'type': 'view' if row[1] == 'VIEW' else 'table'}

    def fetch_columns(self, schema_name, table_name):
        logger.debug('fetch_columns %s %s', schema_name, table_name)

        sql = (
            'SELECT column_name, data_type, udt_name, character_maximum_length, ordinal_position '
            + 'FROM information_schema.columns '
            + f'WHERE table_schema = {self.escape_string(schema_name)} '
            + f'AND table_name = {self.escape_string(table_name)}'
        )

        logger.debug('sql = "%s"', sql)

        try:
            rows = self.fetchall(sql)
        except ProgrammingError as e:
            logger.error('Could not fetch columns from %s.%s (%s)', schema_name, table_name, e)
            return []
        else:
            columns = []
            for row in rows:
                columns.append(self._parse_column(row))

            sql = (
                'SELECT indexdef FROM pg_indexes '
                + f'WHERE schemaname = {self.escape_string(schema_name)} '
                + f'AND tablename = {self.escape_string(table_name)}'
            )

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
        sql = (
            'SELECT column_name, data_type, udt_name, character_maximum_length, ordinal_position '
            + 'FROM information_schema.columns '
            + f'WHERE table_schema = {self.escape_string(schema_name)} '
            + f'AND table_name = {self.escape_string(table_name)} '
            + f'AND column_name = {self.escape_string(column_name)}'
        )

        logger.debug('sql = "%s"', sql)

        try:
            row = self.fetchone(sql)
        except ProgrammingError as e:
            logger.error('Could not fetch %s.%s.%s (%s)', schema_name, table_name, column_name, e)
            return {}
        else:
            if row is None:
                logger.info(
                    'Could not fetch %s.%s.%s. Check if the schema exists.',
                    schema_name,
                    table_name,
                    column_name,
                )
                return {}
            else:
                column = self._parse_column(row)

            sql = (
                'SELECT indexdef FROM pg_indexes '
                + f'WHERE schemaname = {self.escape_string(schema_name)} '
                + f'AND tablename = {self.escape_string(table_name)}'
            )

            logger.debug('sql = "%s"', sql)

            try:
                rows = self.fetchall(sql)
            except OperationalError as e:
                logger.error(
                    'Could not fetch indexes of %s.%s.%s (%s)',
                    schema_name,
                    table_name,
                    column_name,
                    e,
                )
                return column
            else:
                columnname = '({})'.format(column['name'])
                if str(rows).replace('"', '').find(columnname) > -1:
                    column['indexed'] = True

            return column

    def fetch_column_names(self, schema_name, table_name):
        logger.debug('schema_name = "%s"', schema_name)
        logger.debug('table_name = "%s"', table_name)

        sql = (
            'SELECT column_name FROM information_schema.columns '
            + f'WHERE table_schema = {self.escape_string(schema_name)} '
            + f'AND table_name = {self.escape_string(table_name)}'
        )

        logger.debug('sql = "%s"', sql)
        return [column[0] for column in self.fetchall(sql)]

    def fetch_columns_sync(self, database_columns):

        type_oids = {col.type_code for col in database_columns}

        sql = f"""
        SELECT oid, typname, format_type(oid, NULL)
        FROM pg_type
        WHERE oid IN ({",".join(str(oid) for oid in type_oids)})
        """

        logger.debug('sql = "%s"', sql)
        try:
            type_map = {oid: (typname, data_type) for oid, typname, data_type in self.fetchall(sql)}
        except ProgrammingError as e:
            logger.error('Could not fetch (%s)', e)
            return []
        else:
            if type_map is None:
                logger.info(
                    'Could not fetch the columns. Check if the schema exists.'
                )
                return []
            else:
                tm = type_map
                parse = self._parse_column
                columns = []
                append = columns.append
                none = None

                for i, col in enumerate(database_columns, start=1):
                    udt_name, data_type = tm[col.type_code]
                    append(parse((col.name, data_type, udt_name, none, i)))

                return columns

    def create_table(self, schema_name, table_name, columns):
        for column in columns:
            if self.COLUMNTYPES.get(column['datatype']) is None:
                raise TypeError(
                    'Column {name} is of type {datatype}. {datatype} is not '.format(**column)
                    + 'supported by Postgres, the table can not be created.'
                )
        sql = 'CREATE TABLE {schema}.{table} ({columns})'.format(
            schema=self.escape_identifier(schema_name),
            table=self.escape_identifier(table_name),
            columns=', '.join(
                [
                    '{column_name} {column_type}{ar}'.format(
                        column_name=self.escape_identifier(column['name']),
                        column_type=self.COLUMNTYPES[column['datatype']],
                        ar='[]'
                        if column['arraysize']
                        and self.DATATYPES[self.COLUMNTYPES[column['datatype']]]['arraysize']
                        else '',
                    )
                    for column in columns
                ]
            ),
        )

        if settings.USER_TABLESPACE is not None:
            sql += f' TABLESPACE {settings.USER_TABLESPACE}'

        sql += ';'

        logger.debug('sql = "%s"', sql)
        self.execute(sql)

    def rename_table(self, schema_name, table_name, new_table_name):
        sql = (
            f'ALTER TABLE {self.escape_identifier(schema_name)}.{self.escape_identifier(table_name)} '  # noqa: E501
            + f'RENAME TO {self.escape_identifier(new_table_name)};'
        )

        logger.debug('sql = "%s"', sql)
        self.execute(sql)

    def trim_table_rows(self, schema_name, table_name, max_records):
        if not self.table_exists(schema_name, table_name):
            return

        query = (
            'DELETE FROM '
            + f'{self.escape_identifier(schema_name)}.{self.escape_identifier(table_name)} '
            + 'WHERE ctid NOT IN (SELECT ctid FROM '
            + f'{self.escape_identifier(schema_name)}.{self.escape_identifier(table_name)} '
            + f'LIMIT {max_records} );'
        )
        self.execute(query)

    def table_exists(self, schema_name, table_name):
        check_query = (
            'SELECT EXISTS (SELECT 1 FROM information_schema.tables '
            + 'WHERE table_schema = %s AND table_name = %s);'
        )
        return self.fetchone(check_query, (schema_name, table_name))[0]

    def _process_ordering(self, sql, ordering, escaped_column_names):
        if ordering:
            if ordering.startswith('-'):
                escaped_ordering_column, ordering_direction = (
                    self.escape_identifier(ordering[1:]),
                    'DESC',
                )
            else:
                escaped_ordering_column, ordering_direction = (
                    self.escape_identifier(ordering),
                    'ASC',
                )

            if escaped_ordering_column in escaped_column_names:
                sql += f' ORDER BY {escaped_ordering_column} {ordering_direction}'

        return sql

    def _parse_column(self, row):
        column_name, data_type, udt_name, character_maximum_length, ordinal_position = row

        column = {'name': column_name}

        if udt_name.lower() in self.DATATYPES:  # universal types: int2, int4, int8, _float8, ...
            datatype = self.DATATYPES[udt_name.lower()]

        elif data_type.lower() in self.DATATYPES:  # postgres types: smallint, bigint, ARRAY, ...
            datatype = self.DATATYPES[data_type.lower()]

        else:
            datatype = None

        if datatype:
            if '_' in udt_name.lower():  # ARRAY
                column['datatype'] = (
                    datatype['datatype'] + '[]'
                )  # the _ is still needed, will be removed by the serializer.
                column['arraysize'] = None

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

        logger.debug('row = %s', row)
        logger.debug('column = %s', column)
        return column
