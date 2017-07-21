from .base import DatabaseAdapter


class MySQLAdapter(DatabaseAdapter):

    FUNCTIONS = (
        # group_functions
        'AVG', 'COUNT', 'MAX_SYM', 'MIN_SYM', 'SUM', 'BIT_AND', 'BIT_OR', 'BIT_XOR',
        'BIT_COUNT', 'GROUP_CONCAT', 'STD', 'STDDEV', 'STDDEV_POP', 'STDDEV_SAMP',
        'VAR_POP', 'VAR_SAMP', 'VARIANCE',
        # number_functions
        'ABS', 'ACOS', 'ASIN', 'ATAN2', 'ATAN', 'CEIL', 'CEILING', 'CONV', 'COS', 'COT',
        'CRC32', 'DEGREES', 'EXP', 'FLOOR', 'LN', 'LOG10', 'LOG2', 'LOG', 'MOD', 'PI', 'POW'
        'POWER', 'RADIANS', 'RAND', 'ROUND', 'SIGN', 'SIN', 'SQRT', 'TAN', 'TRUNCATE',
        # time_functions
        'ADDDATE', 'ADDTIME', 'CONVERT_TZ', 'CURDATE', 'CURTIME', 'DATE_ADD',
        'DATE_FORMAT', 'DATE_SUB', 'DATE_SYM', 'DATEDIFF', 'DAYNAME', 'DAYOFMONTH',
        'DAYOFWEEK', 'DAYOFYEAR', 'EXTRACT', 'FROM_DAYS', 'FROM_UNIXTIME', 'GET_FORMAT',
        'HOUR', 'LAST_DAY', 'MAKEDATE', 'MAKETIME', 'MICROSECOND', 'MINUTE', 'MONTH',
        'MONTHNAME', 'NOW', 'PERIOD_ADD', 'PERIOD_DIFF', 'QUARTER', 'SEC_TO_TIME',
        'SECOND', 'STR_TO_DATE', 'SUBTIME', 'SYSDATE', 'TIME_FORMAT', 'TIME_TO_SEC',
        'TIME_SYM', 'TIMEDIFF', 'TIMESTAMP', 'TIMESTAMPADD', 'TIMESTAMPDIFF', 'TO_DAYS',
        'TO_SECONDS', 'UNIX_TIMESTAMP', 'UTC_DATE', 'UTC_TIME', 'UTC_TIMESTAMP', 'WEEK',
        'WEEKDAY', 'WEEKOFYEAR', 'YEAR', 'YEARWEEK',
    )

    ENGINE = 'MyISAM'

    def fetch_pid(self):
        return self.connection().connection.thread_id()

    def escape_identifier(self, identifier):
        # escape backticks whithin the identifier and backtick the string
        return '`%s`' % identifier.replace('`', '``')

    def escape_string(self, string):
        return "'%s'" % string

    def build_query(self, database_name, table_name, query, timeout):
        # construct the actual query
        return 'SET STATEMENT max_statement_time=%(timeout)s FOR CREATE TABLE %(database)s.%(table)s ENGINE=%(engine)s ( %(query)s );' % {
            'timeout': timeout,
            'database': self.escape_identifier(database_name),
            'table': self.escape_identifier(table_name),
            'engine': self.ENGINE,
            'query': query,
        }

    def abort_query(self, pid):
        sql = 'KILL %(pid)i' % {'pid': pid}
        self.execute(sql)

    def count_rows(self, database_name, table_name, column_names=None, filter_string=None):
        # prepare sql string
        sql = 'SELECT COUNT(*) FROM %(database)s.%(table)s' % {
            'database': self.escape_identifier(database_name),
            'table': self.escape_identifier(table_name)
        }

        # process filtering
        if filter_string:
            # create a list of escaped columns
            escaped_column_names = [self.escape_identifier(column_name) for column_name in column_names]

            sql_args = []
            where_stmts = []
            for escaped_column_name in escaped_column_names:
                sql_args.append('%' + filter_string + '%')
                where_stmts.append(escaped_column_name + ' LIKE %s')

            sql += ' WHERE ' + ' OR '.join(where_stmts)
        else:
            sql_args = None

        return self.fetchone(sql, args=sql_args)[0]

    def fetch_stats(self, database_name, table_name):
        sql = 'SELECT table_rows as nrows, data_length + index_length AS size FROM `information_schema`.`tables` WHERE `table_schema` = %s AND table_name = %s;'
        return self.fetchone(sql, (database_name, table_name))

    def fetch_rows(self, database_name, table_name, column_names, ordering=None, page=1, page_size=10, filter_string=None):
        # create a list of escaped columns
        escaped_column_names = [self.escape_identifier(column_name) for column_name in column_names]

        # prepare sql string
        sql = 'SELECT %(columns)s FROM %(database)s.%(table)s' % {
            'database': self.escape_identifier(database_name),
            'table': self.escape_identifier(table_name),
            'columns': ', '.join(escaped_column_names)
        }

        # process filtering
        if filter_string:
            sql_args = []
            where_stmts = []
            for escaped_column_name in escaped_column_names:
                sql_args.append('%' + filter_string + '%')
                where_stmts.append(escaped_column_name + ' LIKE %s')

            sql += ' WHERE ' + ' OR '.join(where_stmts)
        else:
            sql_args = None

        # process ordering
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

        # process page and page_size
        sql += ' LIMIT %(limit)s OFFSET %(offset)s' % {
            'limit': page_size,
            'offset': (int(page) - 1) * int(page_size)
        }

        return self.fetchall(sql, args=sql_args)

    def create_user_database_if_not_exists(self, database_name):
        # escape input
        escaped_database_name = self.escape_identifier(database_name)

        # prepare sql string
        sql = 'CREATE DATABASE IF NOT EXISTS %(database)s' % {
            'database': escaped_database_name
        }

        self.execute(sql)

    def fetch_tables(self, database_name):
        # escape input
        escaped_database_name = self.escape_identifier(database_name)

        # prepare sql string
        sql = 'SHOW FULL TABLES FROM %(database)s' % {
            'database': escaped_database_name
        }

        # execute query
        rows = self.fetchall(sql)

        return [{
            'name': row[0],
            'type': 'view' if row[1] == 'VIEW' else 'table'
        } for row in rows]

    def fetch_table(self, database_name, table_name):
        # prepare sql string
        sql = 'SHOW FULL TABLES FROM %(database)s LIKE %(table)s' % {
            'database': self.escape_identifier(database_name),
            'table': self.escape_string(table_name)
        }

        # execute query
        row = self.fetchone(sql)

        return {
            'name': row[0],
            'type': 'view' if row[1] == 'VIEW' else 'table'
        }

    def rename_table(self, database_name, table_name, new_table_name):
        sql = 'RENAME TABLE %(database)s.%(table)s to %(database)s.%(new_table)s;' % {
            'database': self.escape_identifier(database_name),
            'table': self.escape_identifier(table_name),
            'new_table': self.escape_identifier(new_table_name)
        }

        self.execute(sql)

    def drop_table(self, database_name, table_name):
        sql = 'DROP TABLE IF EXISTS %(database)s.%(table)s;' % {
            'database': self.escape_identifier(database_name),
            'table': self.escape_identifier(table_name)
        }

        self.execute(sql)

    def fetch_columns(self, database_name, table_name):
        # prepare sql string
        sql = 'SHOW FULL COLUMNS FROM %(database)s.%(table)s;' % {
            'database': self.escape_identifier(database_name),
            'table': self.escape_identifier(table_name)
        }

        # execute query
        rows = self.fetchall(sql)

        return [{
            'name': row[0],
            'datatype': row[1],
            'indexed': bool(row[4])
        } for row in rows]

    def fetch_column(self, database_name, table_name, column_name):
        # prepare sql string
        sql = 'SHOW FULL COLUMNS FROM %(database)s.%(table)s WHERE `Field` = %(column)s' % {
            'database': self.escape_identifier(database_name),
            'table': self.escape_identifier(table_name),
            'column': self.escape_string(column_name)
        }

        # execute query
        row = self.fetchone(sql)

        return {
            'name': row[0],
            'datatype': row[1],
            'indexed': bool(row[4])
        }

    def fetch_column_names(self, database_name, table_name):
        # prepare sql string
        sql = 'SHOW COLUMNS FROM %(database)s.%(table)s' % {
            'database': self.escape_identifier(database_name),
            'table': self.escape_identifier(table_name),
        }
        return [column[0] for column in self.fetchall(sql)]
