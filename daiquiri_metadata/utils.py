import json
import re

from django.db import connections, OperationalError


def store_table_comment(database_name, table_name, table_metadata):

    with connections['metadata'].cursor() as cursor:
        try:
            cursor.execute("ALTER TABLE `%s`.`%s` COMMENT '%s';" % (database_name, table_name, json.dumps(table_metadata)))
        except OperationalError:
            pass


def store_column_comment(database_name, table_name, column_name, column_metadata):

    with connections['metadata'].cursor() as cursor:
        cursor.execute('SHOW CREATE TABLE `%s`.`%s`;' % (database_name, table_name))

        column_options = False
        for line in cursor.fetchone()[1].split('\n'):
            if line.strip().startswith('`%s`' % column_name):
                column_options = line.strip().strip(',').split('COMMENT')[0]
                break

        if column_options:
            cursor.execute("ALTER TABLE `%s`.`%s` CHANGE `%s` %s COMMENT '%s';" % (
                database_name,
                table_name,
                column_name,
                column_options,
                json.dumps(column_metadata))
            )


def _get_table(database_name, row):
    if not row:
        return {}

    with connections['metadata'].cursor() as cursor:
        cursor.execute('SHOW CREATE TABLE `%s`.`%s`;' % (database_name, row[0]))
        match = re.search("COMMENT='({.*?})'", cursor.fetchone()[1])

        if match:
            try:
                table = json.loads(match.group(1))
            except ValueError:
                table = {}
        else:
            table = {}

        if 'name' not in table:
            table['name'] = row[0]

        if 'type' not in table:
            table['type'] = 'view' if row[1] == 'VIEW' else 'table'

        return table


def discover_tables(database_name):
    tables = []

    with connections['metadata'].cursor() as cursor:
        cursor.execute('SHOW FULL TABLES FROM `%s`;' % database_name)
        for row in cursor.fetchall():
            tables.append(_get_table(database_name, row))

    return tables


def discover_table(database_name, table_name):

    with connections['metadata'].cursor() as cursor:
        cursor.execute('SHOW FULL TABLES FROM `%s` LIKE "%s";' % (database_name, table_name))
        return _get_table(database_name, cursor.fetchone())


def _get_column(row):
    if not row:
        return {}

    comment = row[8]

    # handle legacy comments starting with 'DQIMETA='
    if comment.startswith('DQIMETA='):
        comment = comment[8:]

    try:
        column = json.loads(comment)
    except ValueError:
        column = {}

    if 'name' not in column:
        column['name'] = row[0]

    if 'datatype' not in column:
        column['datatype'] = row[1]

    if 'indexed' not in column:
        column['indexed'] = bool(row[4])

    return column


def discover_columns(database_name, table_name):
    columns = []

    with connections['metadata'].cursor() as cursor:
        cursor.execute('SHOW FULL COLUMNS FROM `%s`.`%s`;' % (database_name, table_name))
        rows = cursor.fetchall()
        for row in rows:
            columns.append(_get_column(row))

    return columns


def discover_column(database_name, table_name, column_name):

    with connections['metadata'].cursor() as cursor:
        cursor.execute('SHOW FULL COLUMNS FROM `%s`.`%s` WHERE `Field` = "%s";' % (database_name, table_name, column_name))
        return _get_column(cursor.fetchone())
