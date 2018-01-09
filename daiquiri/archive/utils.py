import os

from django.conf import settings

from daiquiri.core.adapter import get_adapter


def count_rows(collections, column_names, search, filters):
    adapter = get_adapter()

    database_name = settings.ARCHIVE_DATABASE
    table_name = settings.ARCHIVE_TABLE

    if collections:
        filters['collection'] = collections
        return adapter.database.count_rows(database_name, table_name, column_names, search, filters)
    else:
        return 0


def fetch_rows(collections, column_names, ordering, page, page_size, search, filters):
    adapter = get_adapter()

    database_name = settings.ARCHIVE_DATABASE
    table_name = settings.ARCHIVE_TABLE

    if collections:
        filters['collection'] = collections
        return adapter.database.fetch_rows(database_name, table_name, column_names, ordering, page, page_size, search, filters)
    else:
        return []


def fetch_row(collections, column_names, row_id):
    adapter = get_adapter()

    database_name = settings.ARCHIVE_DATABASE
    table_name = settings.ARCHIVE_TABLE

    return adapter.database.fetch_row(database_name, table_name, column_names, filters={
        'id': row_id,
        'collection': collections
    })
