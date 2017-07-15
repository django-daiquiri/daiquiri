class DatabaseAdapter(object):

    def execute(self, sql):
        return self.cursor.execute(sql)

    def fetchone(self, sql, args=None):
        if args:
            self.cursor.execute(sql, args)
        else:
            self.cursor.execute(sql)

        return self.cursor.fetchone()

    def fetchall(self, sql, args=None):
        if args:
            self.cursor.execute(sql, args)
        else:
            self.cursor.execute(sql)

        return self.cursor.fetchall()

    def fetch_pid(self):
        raise NotImplementedError()

    def escape_identifier(self, identifier):
        raise NotImplementedError()

    def escape_string(self, string):
        raise NotImplementedError()

    def build_query(self, database_name, table_name, query):
        raise NotImplementedError()

    def kill_query(self, pid):
        raise NotImplementedError()

    def count_rows(self, database_name, table_name, column_names=None, filter_string=None):
        raise NotImplementedError()

    def fetch_rows(self, database_name, table_name, column_names, ordering=None, page=1, page_size=10, filter_string=None):
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
