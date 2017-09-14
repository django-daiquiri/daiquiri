from django.db import connections


class DatabaseAdapter(object):

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

    def build_query(self, database_name, table_name, query, timeout):
        raise NotImplementedError()

    def abort_query(self, pid):
        raise NotImplementedError()

    def count_rows(self, database_name, table_name, column_names=None, filter_string=None):
        raise NotImplementedError()

    def fetch_rows(self, database_name, table_name, column_names=None, ordering=None, page=1, page_size=10, filter_string=None):
        raise NotImplementedError()

    def fetch_row(self, database_name, table_name, column_name, value):
        raise NotImplementedError()

    def create_user_database_if_not_exists(self, database_name):
        raise NotImplementedError()

    def fetch_tables(self, database_name):
        raise NotImplementedError()

    def fetch_table(self, database_name, table_name):
        raise NotImplementedError()

    def rename_table(self, database_name, table_name, new_table_name):
        raise NotImplementedError()

    def drop_table(self, database_name, table_name):
        raise NotImplementedError()

    def fetch_columns(self, database_name, table_name):
        raise NotImplementedError()

    def fetch_column(self, database_name, table_name, column_name):
        raise NotImplementedError()

    def fetch_column_names(self, database_name, table_name):
        raise NotImplementedError()
