from django.conf import settings

from daiquiri.metadata.models import Schema, Table, Column


def get_user_columns(user, schema_name, table_name):
    # check permissions on the schema
    try:
        schema = Schema.objects.filter_by_access_level(user).get(name=schema_name)
    except Schema.DoesNotExist:
        return []

    # check permissions on the table
    try:
        table = Table.objects.filter_by_access_level(user).filter(schema=schema).get(name=table_name)
    except Table.DoesNotExist:
        return []

    # get columns for this table
    if settings.METADATA_COLUMN_PERMISSIONS:
        return Column.objects.filter_by_access_level(user).filter(table=table)
    else:
        return Column.objects.filter(table=table)
