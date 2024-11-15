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
            return 'SET STATEMENT max_statement_time={timeout} FOR CREATE TABLE {schema}.{table} ENGINE=ARIA ( {query} ) LIMIT {max_records};'.format(**params)  # noqa: E501
        else:
            return 'SET STATEMENT max_statement_time={timeout} FOR CREATE TABLE {schema}.{table} ENGINE=ARIA ( {query} );'.format(**params)  # noqa: E501

    def build_sync_query(self, query, timeout, max_records):
        # construct the actual query
        params = {
            'query': query,
            'timeout': timeout,
            'max_records': max_records
        }

        if max_records is not None:
            return 'SET STATEMENT max_statement_time={timeout} FOR {query} LIMIT {max_records};'.format(**params)
        else:
            return 'SET STATEMENT max_statement_time={timeout} FOR {query};'.format(**params)
