from .mysql import MySQLAdapter


class MariaDBAdapter(MySQLAdapter):

    def build_query(self, database_name, table_name, query, timeout):
        # construct the actual query
        return 'SET STATEMENT max_statement_time=%(timeout)s FOR CREATE TABLE %(database)s.%(table)s ENGINE=ARIA ( %(query)s );' % {
            'timeout': timeout,
            'database': self.escape_identifier(database_name),
            'table': self.escape_identifier(table_name),
            'query': query
        }
