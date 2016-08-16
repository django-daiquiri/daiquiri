from django.conf import settings
from django.db import connections


def get_adapter(database_config):
    if database_config in settings.DATABASES:
        if settings.DATABASES[database_config]['ENGINE'] == 'django.db.backends.mysql':
            return MySQLAdapter(database_config)
        else:
            raise Exception('database engine "%s" is not supported (yet)' % settings.DATABASES[database_config]['ENGINE'])
    else:
        raise Exception('no database config named "%s" found in settings.DATABASES' % database_config)


class BaseAdapter(object):

    def fetchone(self, sql, args=None):
        if args:
            self.cursor.execute(sql, args)
        else:
            self.cursor.execute(sql)

        return self.cursor.fetchone()[0]

    def fetchall(self, sql, args=None):
        if args:
            self.cursor.execute(sql, args)
        else:
            self.cursor.execute(sql)

        return self.cursor.fetchall()


class MySQLAdapter(BaseAdapter):

    def __init__(self, database_config):
        self.connection = connections[database_config]
        self.cursor = self.connection.cursor()

    def escape_identifier(self, identifier):
        return '`%s`' % identifier

    def count_rows(self, database, table):
        # prepare sql string
        sql = 'SELECT COUNT(*) FROM %(database)s.%(table)s' % {
            'database': self.escape_identifier(database.name),
            'table': self.escape_identifier(table.name)
        }

        return self.fetchone(sql)

    def fetch_rows(self, database, table, columns, ordering=None, page=1, page_size=10):

        # create a list of escaped columns
        escaped_column_names = [self.escape_identifier(column.name) for column in columns]

        # prepare sql string
        sql = 'SELECT %(columns)s FROM %(database)s.%(table)s' % {
            'database': self.escape_identifier(database.name),
            'table': self.escape_identifier(table.name),
            'columns': ', '.join(escaped_column_names)
        }

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

        return self.fetchall(sql)
