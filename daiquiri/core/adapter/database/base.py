import six

from django.db import connections


class BaseDatabaseAdapter(object):

    def __init__(self, database_key, database_config):
        self.database_key = database_key
        self.database_config = database_config

    def connection(self):
        return connections[self.database_key]

    def execute(self, sql):
        return self.connection().cursor().execute(sql)

    def fetchone(self, sql, args=None):
        cursor = self.connection().cursor()

        if args:
            cursor.execute(sql, args)
        else:
            cursor.execute(sql)

        return cursor.fetchone()

    def fetchall(self, sql, args=None):
        cursor = self.connection().cursor()

        if args:
            cursor.execute(sql, args)
        else:
            cursor.execute(sql)

        return cursor.fetchall()

    def fetch_pid(self):
        raise NotImplementedError()

    def escape_identifier(self, identifier):
        raise NotImplementedError()

    def escape_string(self, string):
        raise NotImplementedError()

    def build_query(self, schema_name, table_name, query, timeout):
        raise NotImplementedError()

    def abort_query(self, pid):
        raise NotImplementedError()

    def count_rows(self, schema_name, table_name, column_names=None, search=None, filters=None):
        raise NotImplementedError()

    def fetch_rows(self, schema_name, table_name, column_names=None, ordering=None, page=1, page_size=10, search=None, filters=None):
        raise NotImplementedError()

    def fetch_row(self, schema_name, table_name, column_name, value):
        raise NotImplementedError()

    def create_user_schema_if_not_exists(self, schema_name):
        raise NotImplementedError()

    def fetch_tables(self, schema_name):
        raise NotImplementedError()

    def fetch_table(self, schema_name, table_name):
        raise NotImplementedError()

    def rename_table(self, schema_name, table_name, new_table_name):
        raise NotImplementedError()

    def drop_table(self, schema_name, table_name):
        raise NotImplementedError()

    def fetch_columns(self, schema_name, table_name):
        raise NotImplementedError()

    def fetch_column(self, schema_name, table_name, column_name):
        raise NotImplementedError()

    def fetch_column_names(self, schema_name, table_name):
        raise NotImplementedError()

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
                if isinstance(column_filter, six.string_types):
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
