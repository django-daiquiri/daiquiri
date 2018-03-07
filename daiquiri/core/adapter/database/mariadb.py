from .mysql import MySQLAdapter


class MariaDBAdapter(MySQLAdapter):

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
            return 'SET STATEMENT max_statement_time=%(timeout)s FOR CREATE TABLE %(schema)s.%(table)s ENGINE=ARIA ( %(query)s ) LIMIT %(max_records)s;' % params
        else:
            return 'SET STATEMENT max_statement_time=%(timeout)s FOR CREATE TABLE %(schema)s.%(table)s ENGINE=ARIA ( %(query)s );' % params
