import json
import re

from django.db import connections, OperationalError


def discover_tables(database_name):
    tables = []

    with connections['metadata'].cursor() as cursor:
        cursor = connections['metadata'].cursor()
        cursor.execute('SHOW FULL TABLES FROM %s;' % database_name)
        rows = cursor.fetchall()

    for row in rows:
        table_name = row[0]

        cursor.execute('SHOW CREATE TABLE `%s`.`%s`;' % (database_name, table_name))
        match = re.search("COMMENT='({.*?})'", cursor.fetchone()[1])

        if match:
            try:
                table = json.loads(match.group(1))
            except ValueError:
                table = {}
        else:
            table = {}

        if 'name' not in table:
            table['name'] = table_name

        if 'type' not in table:
            table['type'] = 'view' if row[1] == 'VIEW' else 'table'

        tables.append(table)

    return tables


def discover_columns(database_name, table_name):
    columns = []

    with connections['metadata'].cursor() as cursor:
        cursor = connections['metadata'].cursor()
        cursor.execute('SHOW FULL COLUMNS FROM %s FROM %s;' % (table_name, database_name))
        rows = cursor.fetchall()

    for row in rows:
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

        columns.append(column)

    return columns


def store_table_comment(database_name, table_name, table_metadata):

    with connections['metadata'].cursor() as cursor:
        cursor = connections['metadata'].cursor()

        try:
            cursor.execute("ALTER TABLE `%s`.`%s` COMMENT '%s';" % (
                database_name,
                table_name,
                json.dumps(table_metadata))
            )
        except OperationalError:
            pass


def store_column_comment(database_name, table_name, column_name, column_metadata):

    with connections['metadata'].cursor() as cursor:
        cursor = connections['metadata'].cursor()
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
