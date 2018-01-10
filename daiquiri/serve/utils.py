from django.conf import settings

from daiquiri.core.utils import import_class
from daiquiri.metadata.models import Database, Table, Column


def get_columns(user, database_name, table_name, column_names=None):

    # check permissions on the database
    try:
        database = Database.objects.filter_by_access_level(user).get(name=database_name)
    except Database.DoesNotExist:
        return []

    # check permissions on the table
    try:
        table = Table.objects.filter_by_access_level(user).filter(database=database).get(name=table_name)
    except Table.DoesNotExist:
        return []

    # get columns for this table
    if settings.METADATA_COLUMN_PERMISSIONS:
        columns = Column.objects.filter_by_access_level(user).filter(table=table)
    else:
        columns = Column.objects.filter(table=table)

    # filter by input column names
    if column_names:
        return [column for column in columns if column.name in column_names]
    else:
        return [column for column in columns]


def get_column(user, database_name, table_name, column_name):

    columns = get_columns(user, database_name, table_name)

    try:
        return [column for column in columns if column.name == column_name][0]
    except IndexError:
        # column_name is not in columns
        return None


def get_resolver():
    if settings.SERVE_RESOLVER:
        return import_class(settings.SERVE_RESOLVER)()
    else:
        return None
