from django.db import connections


class DatabaseAdapter(object):


    FUNCTIONS = (
        # char_functions
       'ASCII_SYM', 'BIN', 'BIT_LENGTH', 'CHAR_LENGTH', 'CHAR', 'CONCAT_WS', 'CONCAT',
       'ELT', 'EXPORT_SET', 'FIELD', 'FIND_IN_SET', 'FORMAT', 'FROM_BASE64', 'HEX',
       'INSERT', 'INSTR', 'LEFT', 'LENGTH', 'LOAD_FILE', 'LOCATE', 'LOWER', 'LPAD', 
       'LTRIM', 'MAKE_SET', 'MID', 'OCT', 'ORD', 'QUOTE', 'REPEAT', 'REPLACE', 'REVERSE',
       'RIGHT', 'RPAD', 'RTRIM', 'SOUNDEX', 'SPACE', 'STRCMP', 'SUBSTRING_INDEX',
       'SUBSTRING', 'TO_BASE64', 'TRIM', 'UNHEX', 'UPPER', 'WEIGHT_STRING',

        # group_functions
        'AVG', 'COUNT', 'MAX_SYM', 'MIN_SYM', 'SUM', 'BIT_AND', 'BIT_OR', 'BIT_XOR',
        'BIT_COUNT', 'GROUP_CONCAT', 'STD', 'STDDEV', 'STDDEV_POP', 'STDDEV_SAMP',
        'VAR_POP', 'VAR_SAMP', 'VARIANCE',

        # number_functions
        'ABS', 'ACOS', 'ASIN', 'ATAN2', 'ATAN', 'CEIL', 'CEILING', 'CONV', 'COS', 'COT',
        'CRC32', 'DEGREES', 'EXP', 'FLOOR', 'LN', 'LOG10', 'LOG2', 'LOG', 'MOD', 'PI', 'POW',
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

    def count_rows(self, database_name, table_name, column_names=None, search=None, filters=None):
        raise NotImplementedError()

    def fetch_rows(self, database_name, table_name, column_names=None, ordering=None, page=1, page_size=10, search=None, filters=None):
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
