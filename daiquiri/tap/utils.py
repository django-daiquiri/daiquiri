from django.conf import settings

from daiquiri.core.constants import ACCESS_LEVEL_INTERNAL, ACCESS_LEVEL_PUBLIC

from .models import Column as TapColumn
from .models import Schema as TapSchema
from .models import Table as TapTable


def check_tap_visibility(obj):
    # check if the metadata_access_level of the object is
    #   (a) PUBLIC or INTERNAL if QUERY_ANONYMOUS is True
    # or
    #   (b) INTERNAL if QUERY_ANONYMOUS is False
    return (obj.metadata_access_level == ACCESS_LEVEL_PUBLIC) or \
        (obj.metadata_access_level == ACCESS_LEVEL_INTERNAL and not settings.QUERY_ANONYMOUS)


def update_schema(schema):
    '''
    Update or create the schema in the TAP_SCHEMA.
    '''
    if check_tap_visibility(schema):
        tap_schema, created = TapSchema.objects.get_or_create(pk=schema.id)

        tap_schema.schema_name = schema.name
        tap_schema.utype = None
        if schema.description:
            tap_schema.description = schema.description[:255]
        tap_schema.save()

        if created:
            # call the handler for each table of the schema
            for table in schema.tables.all():
                update_table(table)

    else:
        # remove the schema from the TAP_SCHEMA (if it exists)
        try:
            tap_schema = TapSchema.objects.get(pk=schema.id)
            tap_schema.delete()

            # remove tables and columns
            for tap_table in tap_schema.tables.all():
                tap_table.columns.all().delete()
                tap_table.delete()

        except TapSchema.DoesNotExist:
            pass


def delete_schema(schema):
    '''
    Remove the schema from the TAP_SCHEMA (if it exists).
    '''
    try:
        TapSchema.objects.get(pk=schema.id).delete()
    except TapSchema.DoesNotExist:
        pass


def update_table(table):
    '''
    Update or create the table in the TAP_SCHEMA.
    '''

    # get the schema from the TAP_SCHEMA
    try:
        tap_schema = TapSchema.objects.get(pk=table.schema.id)
    except TapSchema.DoesNotExist:
        tap_schema = None

    if check_tap_visibility(table) and tap_schema:
        tap_table, created = TapTable.objects.get_or_create(pk=table.id, defaults={'schema': tap_schema})

        tap_table.schema_name = str(table.schema)
        tap_table.table_name = str(table.schema) + '.' + str(table.name)
        tap_table.table_type = table.type
        tap_table.utype = table.utype
        if table.description:
            tap_table.description = table.description[:255]
        tap_table.table_index = table.order
        tap_table.save()

        if created:
            # call the handler for each table of the schema
            for column in table.columns.all():
                update_column(column)

    else:
        # remove the table from the TAP_SCHEMA (if it exists)
        try:
            tap_table = TapTable.objects.get(pk=table.id)
            tap_table.delete()

            # remove columns
            tap_table.columns.all().delete()
        except TapTable.DoesNotExist:
            pass


def delete_table(table):
    '''
    Remove the table from the TAP_SCHEMA (if it exists).
    '''
    try:
        TapTable.objects.get(pk=table.id).delete()
    except TapTable.DoesNotExist:
        pass


def update_column(column):
    '''
    Update or create the column in the TAP_SCHEMA.
    '''
    if settings.METADATA_COLUMN_PERMISSIONS:
        tap_visibility = check_tap_visibility(column)
    else:
        tap_visibility = check_tap_visibility(column.table)

    # get the table from the TAP_SCHEMA
    try:
        tap_table = TapTable.objects.get(pk=column.table.id)
    except TapTable.DoesNotExist:
        tap_table = None

    if tap_visibility and tap_table:
        try:
            tap_column = TapColumn.objects.get(pk=column.id)
            tap_column.table = tap_table
        except TapColumn.DoesNotExist:
            tap_column = TapColumn.objects.create(pk=column.id, table=tap_table)

        tap_column.table_name = str(column.table)
        tap_column.column_name = column.name
        tap_column.datatype = column.datatype
        tap_column.arraysize = column.arraysize
        tap_column.size = column.arraysize
        if column.description:
            tap_column.description = column.description[:255]
        tap_column.utype = column.utype
        tap_column.unit = column.unit
        tap_column.ucd = column.ucd
        tap_column.indexed = column.indexed
        tap_column.principal = column.principal
        tap_column.std = column.std
        tap_column.column_index = column.order
        tap_column.save()
    else:
        # remove the column from the TAP_SCHEMA (if it exists)
        try:
            TapColumn.objects.get(pk=column.id).delete()
        except TapColumn.DoesNotExist:
            pass


def delete_column(column):
    '''
    Remove the column from the TAP_SCHEMA (if it exists).
    '''
    try:
        TapColumn.objects.get(pk=column.id).delete()
    except TapColumn.DoesNotExist:
        pass
