import json
import re

from django.db import connections

from .base import BaseAdapter


class MySQLAdapter(BaseAdapter):

    def __init__(self, database_config):
        self.connection = connections[database_config]
        self.cursor = self.connection.cursor()

    def escape_identifier(self, identifier):
        return '`%s`' % identifier

    def escape_string(self, string):
        return "'%s'" % string

    def execute_query(self, query):
        return self.fetchall(query)

    def submit_direct_query(self, database_name, table_name, query):
        # construct the actual query
        sql = 'CREATE TABLE %(database)s.%(table)s ENGINE=MyISAM ( %(query)s );' % {
            'database': self.escape_identifier(database_name),
            'table': self.escape_identifier(table_name),
            'query': query
        }

        self.execute(sql)

        return sql

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

    def fetch_tables(self, database_name):
        # escape input
        escaped_database_name = self.escape_identifier(database_name)

        # prepare sql string
        sql = 'SHOW FULL TABLES FROM %(database)s' % {
            'database': escaped_database_name
        }

        # execute query
        rows = self.fetchall(sql)

        return [self.fetch_table_metadata(database_name, row[0], row[1]) for row in rows]

    def fetch_table(self, database_name, table_name):
        # prepare sql string
        sql = 'SHOW FULL TABLES FROM %(database)s LIKE %(table)s' % {
            'database': self.escape_identifier(database_name),
            'table': self.escape_string(table_name)
        }

        # execute query
        row = self.fetchone(sql)

        return self.fetch_table_metadata(database_name, row[0], row[1])

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

    def fetch_table_metadata(self, database_name, table_name, table_type):
        # prepare sql string
        sql = 'SHOW CREATE TABLE %(database)s.%(table)s' % {
            'database': self.escape_identifier(database_name),
            'table': self.escape_identifier(table_name)
        }

        # execute query
        row = self.fetchone(sql)

        # parse comment metadata json
        match = re.search("COMMENT='({.*?})'", row[1])
        if match:
            try:
                table_metadata = json.loads(match.group(1))
            except ValueError:
                table_metadata = {}
        else:
            table_metadata = {}

        if 'name' not in table_metadata:
            table_metadata['name'] = table_name

        if 'type' not in table_metadata:
            table_metadata['type'] = 'view' if table_type == 'VIEW' else 'table'

        return table_metadata

    def fetch_columns(self, database_name, table_name):
        # prepare sql string
        sql = 'SHOW FULL COLUMNS FROM %(database)s.%(table)s;' % {
            'database': self.escape_identifier(database_name),
            'table': self.escape_identifier(table_name)
        }

        # execute query
        rows = self.fetchall(sql)

        return [self.fetch_column_metadata(row[0], row[1], row[4], row[8]) for row in rows]

    def fetch_column(self, database_name, table_name, column_name):
        # prepare sql string
        sql = 'SHOW FULL COLUMNS FROM %(database)s.%(table)s WHERE `Field` = %(column)s' % {
            'database': self.escape_identifier(database_name),
            'table': self.escape_identifier(table_name),
            'column': self.escape_string(column_name)
        }

        # execute query
        row = self.fetchone(sql)

        return self.fetch_column_metadata(row[0], row[1], row[4], row[8])

    def fetch_column_names(self, database_name, table_name):
        # prepare sql string
        sql = 'SHOW COLUMNS FROM %(database)s.%(table)s' % {
            'database': self.escape_identifier(database_name),
            'table': self.escape_identifier(table_name),
        }
        return [column[0] for column in self.fetchall(sql)]

    def fetch_column_metadata(self, column_name, column_datatype, column_indexed, column_comment):
        # handle legacy comments starting with 'DQIMETA='
        if column_comment.startswith('DQIMETA='):
            column_comment = column_comment[8:]

        try:
            column_metadata = json.loads(column_comment)
        except ValueError:
            column_metadata = {}

        if 'name' not in column_metadata:
            column_metadata['name'] = column_name

        if 'datatype' not in column_metadata:
            column_metadata['datatype'] = column_datatype

        if 'indexed' not in column_metadata:
            column_metadata['indexed'] = bool(column_indexed)

        return column_metadata

    def store_table_metadata(self, database_name, table_name, table_metadata):
        # prepare sql string
        sql = 'ALTER TABLE %(database)s.%(table)s COMMENT %(json)s' % {
            'database': self.escape_identifier(database_name),
            'table': self.escape_identifier(table_name),
            'json': self.escape_string(json.dumps(table_metadata))
        }

        # execute query
        self.execute(sql)

    def store_column_metadata(self, database_name, table_name, column_name, column_metadata):
        # prepare sql string
        sql = 'SHOW CREATE TABLE %(database)s.%(table)s' % {
            'database': self.escape_identifier(database_name),
            'table': self.escape_identifier(table_name)
        }

        # execute query
        row = self.fetchone(sql)

        # parse the create table statement to get the correct column options string
        # e.g. 'double NOT NULL'
        column_options = False
        for line in row[1].split('\n'):
            if line.strip().startswith(self.escape_identifier(column_name)):
                column_options = line.strip().strip(',').split('COMMENT')[0]
                break

        if column_options:
            # prepare sql string
            sql = 'ALTER TABLE %(database)s.%(table)s CHANGE %(column)s %(options)s COMMENT %(json)s' % {
                'database': self.escape_identifier(database_name),
                'table': self.escape_identifier(table_name),
                'column': self.escape_identifier(column_name),
                'options': column_options,
                'json': self.escape_string(json.dumps(column_metadata))
            }

            # execute query
            self.fetchone(sql)
