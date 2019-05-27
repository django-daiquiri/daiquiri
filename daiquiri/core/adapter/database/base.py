import logging
import warnings

from django.db import connections

logger = logging.getLogger(__name__)


class BaseDatabaseAdapter(object):

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

    def count_rows(self, schema_name, table_name, column_names=None, search=None, filters=None):
        # if no column names are provided get all column_names from the table
        if not column_names:
            column_names= self.fetch_column_names(schema_name, table_name)

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
        sql = 'CREATE SCHEMA IF NOT EXISTS %(schema)s' % {
            'schema': escaped_schema_name
        }

        # log sql string
        logger.debug('sql = "%s"', sql)

        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            self.execute(sql)

    def create_table(self, schema_name, table_name, columns):
        # prepare sql string
        sql = 'CREATE TABLE %(schema)s.%(table)s (%(columns)s);' % {
            'schema': self.escape_identifier(schema_name),
            'table': self.escape_identifier(table_name),
            'columns': ', '.join([
                '%(column_name)s %(column_type)s' % {
                    'column_name': self.escape_identifier(column['name']),
                    'column_type': self.COLUMNTYPES[column['datatype']]
                } for column in columns])
        }

        # log sql string and execute
        logger.debug('sql = "%s"', sql)
        self.execute(sql)

    def rename_table(self, schema_name, table_name, new_table_name):
        raise NotImplementedError()

    def drop_table(self, schema_name, table_name):
        sql = 'DROP TABLE IF EXISTS %(schema)s.%(table)s;' % {
            'schema': self.escape_identifier(schema_name),
            'table': self.escape_identifier(table_name)
        }

        # log sql string and execute
        logger.debug('sql = "%s"', sql)
        self.execute(sql)

    def insert_rows(self, schema_name, table_name, columns, rows):
        # create a list of escaped columns
        escaped_column_names = [self.escape_identifier(column['name']) for column in columns]

        # create a list of escaped value tuples
        escaped_rows = []
        for row in rows:
            # all values are escaped with quotes
            escaped_cells = []
            for column, cell in zip(columns, row):
                if column['datatype'] == 'char':
                    escaped_cells.append(self.escape_string(cell.decode()))
                else:
                    escaped_cells.append(self.escape_string(cell))

            escaped_row = ', '.join(escaped_cells)
            escaped_rows.append('(%s)' % escaped_row)

        # prepare sql string
        sql = 'INSERT INTO %(schema)s.%(table)s (%(columns)s) VALUES %(values)s' % {
            'schema': self.escape_identifier(schema_name),
            'table': self.escape_identifier(table_name),
            'columns': ', '.join(escaped_column_names),
            'values': ', '.join(escaped_rows)
        }

        # log sql string and execute
        logger.debug('sql = "%s"', sql)
        self.execute(sql)

    def _process_filtering(self, sql, sql_args, search, filters, escaped_column_names):
        # prepare lists for the WHERE statements
        where_stmts = []
        where_args = []

        if search:
            # append a OR condition fo every column
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
                # escpae the column_name for this column
                escaped_column_name = self.escape_identifier(column_name)

                # check if the filter is a list or a string
                if isinstance(column_filter, str):
                    filter_list = [column_filter]
                elif isinstance(column_filter, list):
                    filter_list = column_filter
                else:
                    raise RuntimeError('Unsupported filter for column "%s"' % column_name)

                # append a OR condition fo every entry in the list
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
                escaped_ordering_column, ordering_direction = self.escape_identifier(ordering[1:]), 'DESC'
            else:
                escaped_ordering_column, ordering_direction = self.escape_identifier(ordering), 'ASC'

            if escaped_ordering_column in escaped_column_names:
                sql += ' ORDER BY %(column)s %(direction)s' % {
                    'column': escaped_ordering_column,
                    'direction': ordering_direction
                }

        return sql
