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


def get_archive_file_path(user, archive_job_id):
    if not user or user.is_anonymous():
        username = 'anonymous'
    else:
        username = user.username

    directory_name = os.path.join(settings.ARCHIVE_DOWNLOAD_DIR, username)
    return os.path.join(directory_name, str(archive_job_id) + '.zip')
