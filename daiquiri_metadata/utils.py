import json

from django.db import connections


def discover_tables(database_name):
    tables = []

    with connections['metadata'].cursor() as cursor:
        cursor = connections['metadata'].cursor()
        cursor.execute('SHOW FULL TABLES FROM %s;' % database_name)
        rows = cursor.fetchall()

    for row in rows:
        tables.append({
            'name': row[0],
            'type': 'view' if row[1] == 'VIEW' else 'table'
        })

    return tables


def discover_columns(database_name, table_name):
    columns = []

    with connections['metadata'].cursor() as cursor:
        cursor = connections['metadata'].cursor()
        cursor.execute('SHOW FULL COLUMNS FROM %s FROM %s;' % (table_name, database_name))
        rows = cursor.fetchall()

    for row in rows:
        comment = row[8]
        if comment.startswith('DQIMETA='):
            column = json.loads(comment[8:])
        else:
            column = {}

        if 'name' not in column:
            column['name'] = row[0]

        if 'datatype' not in column:
            column['datatype'] = row[1]

        if 'indexed' not in column:
            column['indexed'] = bool(row[4])

        columns.append(column)

    return columns
