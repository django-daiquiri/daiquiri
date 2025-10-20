import logging
import warnings

from django.db import connections

logger = logging.getLogger(__name__)


class BaseDatabaseAdapter:
    def __init__(self, database_key, database_config):
        self.database_key = database_key
        self.database_config = database_config

    def connection(self):
        return connections[self.database_key]

    def execute(self, sql):
        return self.connection().cursor().execute(sql)

    def fetchone(self, sql, args=None, as_dict=False):
        cursor = self.connection().cursor()

        if args:
            cursor.execute(sql, args)
        else:
            cursor.execute(sql)

        if as_dict:
            columns = cursor.description
            row = cursor.fetchone()
            if row:
                return {column.name: value for column, value in zip(columns, row)}
            else:
                return None
        else:
            return cursor.fetchone()

    def fetchall(self, sql, args=None, as_dict=False):
        cursor = self.connection().cursor()

        if args:
            cursor.execute(sql, args)
        else:
            cursor.execute(sql)

        if as_dict:
            columns = cursor.description
            return [
                {column.name: value for column, value in zip(columns, row)}
                for row in cursor.fetchall()
            ]
        else:
            return cursor.fetchall()

    def fetch_pid(self):
        raise NotImplementedError()

    def escape_identifier(self, identifier):
        raise NotImplementedError()

    def escape_string(self, string):
        raise NotImplementedError()

    def build_query(self, schema_name, table_name, query, timeout):
        raise NotImplementedError()

    def build_sync_query(self, query, timeout, max_records):
        raise NotImplementedError()

    def submit_query(self, sql):
        self.execute(sql)

    def abort_query(self, pid):
        raise NotImplementedError()

    def count_rows(
        self, schema_name, table_name, column_names=None, search=None, filters=None
    ):
        # if no column names are provided get all column_names from the table
        if not column_names:
            column_names = self.fetch_column_names(schema_name, table_name)

        # create a list of escaped columns
        escaped_column_names = [
            self.escape_identifier(column_name) for column_name in column_names
        ]

        # prepare sql string
        sql = f'SELECT COUNT(*) FROM {self.escape_identifier(schema_name)}.{self.escape_identifier(table_name)}'
        sql_args = []

        # process filtering
        sql, sql_args = self._process_filtering(
            sql, sql_args, search, filters, escaped_column_names
        )

        return self.fetchone(sql, args=sql_args)[0]

    def fetch_rows(
        self,
        schema_name,
        table_name,
        column_names=None,
        ordering=None,
        page=1,
        page_size=10,
        search=None,
        filters=None,
    ):
        # if no column names are provided get all column_names from the table
        if not column_names:
            column_names = self.fetch_column_names(schema_name, table_name)

        # create a list of escaped columns
        escaped_column_names = [
            self.escape_identifier(column_name) for column_name in column_names
        ]

        # init sql string and sql_args list
        sql = 'SELECT {columns} FROM {schema}.{table}'.format(
            schema=self.escape_identifier(schema_name),
            table=self.escape_identifier(table_name),
            columns=', '.join(escaped_column_names),
        )
        sql_args = []

        # process filtering
        sql, sql_args = self._process_filtering(
            sql, sql_args, search, filters, escaped_column_names
        )

        # process ordering
        sql = self._process_ordering(sql, ordering, escaped_column_names)

        # process page and page_size
        if page_size > 0:
            sql += f' LIMIT {page_size} OFFSET {(int(page) - 1) * int(page_size)}'

        return self.fetchall(sql, args=sql_args)

    def fetch_row(
        self, schema_name, table_name, column_names=None, search=None, filters=None
    ):
        # if no column names are provided get all column_names from the table
        if not column_names:
            column_names = self.fetch_column_names(schema_name, table_name)

        # create a list of escaped columns
        escaped_column_names = [
            self.escape_identifier(column_name) for column_name in column_names
        ]

        # prepare sql string
        sql = 'SELECT {columns} FROM {schema}.{table}'.format(
            schema=self.escape_identifier(schema_name),
            table=self.escape_identifier(table_name),
            columns=', '.join(escaped_column_names),
        )
        sql_args = []

        # process filtering
        sql, sql_args = self._process_filtering(
            sql, sql_args, search, filters, escaped_column_names
        )

        return self.fetchone(sql, args=sql_args)

    def fetch_dict(
        self, schema_name, table_name, column_names=None, search=None, filters=None
    ):
        # if no column names are provided get all column_names from the table
        if not column_names:
            column_names = self.fetch_column_names(schema_name, table_name)

        row = self.fetch_row(schema_name, table_name, column_names, search, filters)

        if row:
            return dict(zip(column_names, row))
        else:
            return {}

    def fetch_size(self, schema_name, table_name):
        raise NotImplementedError()

    def fetch_nrows(self, schema_name, table_name):
        raise NotImplementedError()

    def fetch_tables(self, schema_name):
        raise NotImplementedError()

    def fetch_table(self, schema_name, table_name):
        raise NotImplementedError()

    def fetch_columns(self, schema_name, table_name):
        raise NotImplementedError()

    def fetch_column(self, schema_name, table_name, column_name):
        raise NotImplementedError()

    def fetch_column_names(self, schema_name, table_name):
        raise NotImplementedError()

    def create_user_schema_if_not_exists(self, schema_name):
        # escape input
        escaped_schema_name = self.escape_identifier(schema_name)

        # prepare sql string
        sql = f'CREATE SCHEMA IF NOT EXISTS {escaped_schema_name}'

        # log sql string
        logger.debug('sql = "%s"', sql)

        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            self.execute(sql)

    def create_table(self, schema_name, table_name, columns):
        # check column types
        for column in columns:
            if self.COLUMNTYPES.get(column['datatype']) is None:
                raise TypeError(
                    'Column {name} is of type {datatype}. {datatype} is not '.format(
                        **column
                    )
                    + 'supported by the database, the table can not be created.'
                )

        # prepare sql string
        sql = 'CREATE TABLE {schema}.{table} ({columns});'.format(
            schema=self.escape_identifier(schema_name),
            table=self.escape_identifier(table_name),
            columns=', '.join(
                [
                    '{column_name} {column_type}'.format(
                        column_name=self.escape_identifier(column['name']),
                        column_type=self.COLUMNTYPES[column['datatype']],
                    )
                    for column in columns
                ]
            ),
        )

        # log sql string and execute
        logger.debug('sql = "%s"', sql)
        self.execute(sql)

    def rename_table(self, schema_name, table_name, new_table_name):
        raise NotImplementedError()

    def drop_table(self, schema_name, table_name):
        sql = f'DROP TABLE IF EXISTS {self.escape_identifier(schema_name)}.{self.escape_identifier(table_name)};'

        # log sql string and execute
        logger.debug('sql = "%s"', sql)
        self.execute(sql)

    def insert_rows(self, schema_name, table_name, columns, rows, mask=None):
        # create a list of escaped columns
        escaped_column_names = [
            self.escape_identifier(column['name']) for column in columns
        ]

        # create a list of escaped value tuples
        escaped_rows = []
        if mask is None:
            for row in rows:
                # all values are escaped with quotes
                escaped_cells = []
                for cell in row:
                    escaped_cells.append(self._escape_cell(cell))

                escaped_row = ', '.join(escaped_cells)
                escaped_rows.append(f'({escaped_row})')

        else:
            for row, mask_row in zip(rows, mask):
                # all values are escaped with quotes
                escaped_cells = []
                for cell, mask_cell in zip(row, mask_row):
                    escaped_cells.append(self._escape_cell(cell, mask_cell))

                escaped_row = ', '.join(escaped_cells)
                escaped_rows.append(f'({escaped_row})')

        # prepare sql string
        sql = 'INSERT INTO {schema}.{table} ({columns}) VALUES {values}'.format(
            schema=self.escape_identifier(schema_name),
            table=self.escape_identifier(table_name),
            columns=', '.join(escaped_column_names),
            values=', '.join(escaped_rows),
        )

        # log sql string and execute
        logger.debug('sql = "%s"', sql)
        self.execute(sql)

    def _process_filtering(self, sql, sql_args, search, filters, escaped_column_names):
        # prepare lists for the WHERE statements
        where_stmts = []
        where_args = []

        if search:
            # append a OR condition for every column
            search_stmts = []
            search_args = []
            for escaped_column_name in escaped_column_names:
                # search_stmt_template and search_arg_template are set differently for mysql and postgres
                search_stmts.append(self.search_stmt_template % escaped_column_name)
                search_args.append(self.search_arg_template % search)

            if search_stmts:
                where_stmts.append('(' + ' OR '.join(search_stmts) + ')')
                where_args += search_args

        if filters:
            for column_name, column_filter in filters.items():
                # escape the column_name for this column
                escaped_column_name = self.escape_identifier(column_name)

                # check if the filter is a list or a string
                if isinstance(column_filter, str):
                    filter_list = [column_filter]
                elif isinstance(column_filter, list):
                    filter_list = column_filter
                else:
                    raise RuntimeError(f'Unsupported filter for column "{column_name}"')

                # append a OR condition for every entry in the list
                filter_stmts = []
                filter_args = []
                for filter_string in filter_list:
                    filter_stmts.append(escaped_column_name + ' = %s')
                    filter_args.append(filter_string)

                if filter_stmts:
                    where_stmts.append('(' + ' OR '.join(filter_stmts) + ')')
                    where_args += filter_args

        # connect the where statements with AND and append to the sql string
        if where_stmts:
            sql += ' WHERE ' + ' AND '.join(where_stmts)
            sql_args += where_args

        return sql, sql_args

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

    def _escape_cell(self, cell, mask_cell=None):
        if mask_cell:
            return 'NULL'
        else:
            if hasattr(cell, 'ndim') and cell.ndim == 1:
                # create an array string digestable by postgres
                value_list = [
                    'NULL' if cell.mask[i] else str(cell[i]) for i in range(len(cell))
                ]
                value = '{' + ', '.join(value_list) + '}'
            elif isinstance(cell, str):
                value = cell
            elif cell.dtype.char == 'S':
                # chars need to be decoded
                value = cell.decode()
            elif cell.dtype.char == '?':
                # booleans need to be converted to 0 or 1, or quoting will fail
                value = 1 if cell else 0
            else:
                value = cell

            return self.escape_string(value)
