from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from daiquiri.metadata.models import Database, Table, Column
from daiquiri.metadata.settings import ACCESS_LEVEL_PUBLIC, ACCESS_LEVEL_INTERNAL

from .models import (
    Schema as TapSchema,
    Table as TapTable,
    Column as TapColumn,
)


@receiver(post_save, sender=Database)
def database_updated_handler(sender, **kwargs):

    instance = kwargs['instance']

    # check if the metadata_access_level is public or it matches the TAP_ACCESS_LEVEL
    tap = (instance.metadata_access_level == ACCESS_LEVEL_PUBLIC) or \
        (instance.metadata_access_level == settings.TAP_ACCESS_LEVEL)

    if tap:
        try:
            schema = TapSchema.objects.using('tap').get(pk=instance.id)
        except TapSchema.DoesNotExist:
            schema = TapSchema.objects.using('tap').create(pk=instance.id)

        schema.schema_name = instance.name
        schema.utype = None
        if instance.description:
            schema.description = instance.description[:255]
        schema.save()

    else:
        # remove the database from the TAP_SCHEMA (if it exists)
        try:
            TapSchema.objects.using('tap').get(pk=instance.id).delete()
        except TapSchema.DoesNotExist:
            pass

    # call the handler for each table of the database
    for table in instance.tables.all():
        table_updated_handler(Table, instance=table)


@receiver(post_delete, sender=Database)
def database_deleted_handler(sender, **kwargs):

    instance = kwargs['instance']

    # remove the database from the TAP_SCHEMA (if it exists)
    try:
        TapSchema.objects.using('tap').get(pk=instance.id).delete()
    except TapSchema.DoesNotExist:
        pass


@receiver(post_save, sender=Table)
def table_updated_handler(sender, **kwargs):

    instance = kwargs['instance']

    # check if the metadata_access_level is public or it matches the TAP_ACCESS_LEVEL
    tap = (instance.metadata_access_level == ACCESS_LEVEL_PUBLIC) or \
        (instance.metadata_access_level == settings.TAP_ACCESS_LEVEL)

    # get the schema from the TAP_SCHEMA
    try:
        schema = TapSchema.objects.using('tap').get(pk=instance.database.id)
    except TapSchema.DoesNotExist:
        schema = None

    if tap and schema:
        try:
            table = TapTable.objects.using('tap').get(pk=instance.id)
            table.schema = schema
        except TapTable.DoesNotExist:
            table = TapTable.objects.using('tap').create(pk=instance.id, schema=schema)

        table.schema_name = str(instance.database)
        table.table_name = instance.name
        table.table_type = instance.type
        table.utype = instance.utype
        if instance.description:
            table.description = instance.description[:255]
        table.table_index = instance.order

        table.save()

    else:
        # remove the table from the TAP_SCHEMA (if it exists)
        try:
            TapTable.objects.using('tap').get(pk=instance.id).delete()
        except TapTable.DoesNotExist:
            pass

    # call the handler for each column of the table
    for columns in instance.columns.all():
        column_updated_handler(Column, instance=columns)


@receiver(post_delete, sender=Table)
def table_deleted_handler(sender, **kwargs):

    instance = kwargs['instance']

    # remove the table from the TAP_SCHEMA (if it exists)
    try:
        TapTable.objects.using('tap').get(pk=instance.id).delete()
    except TapTable.DoesNotExist:
        pass


@receiver(post_save, sender=Column)
def column_updated_handler(sender, **kwargs):

    instance = kwargs['instance']

    # check if the metadata_access_level is public or it matches the TAP_ACCESS_LEVEL
    tap = (instance.metadata_access_level == ACCESS_LEVEL_PUBLIC) or \
        (instance.metadata_access_level == settings.TAP_ACCESS_LEVEL)

    # get the table from the TAP_SCHEMA
    try:
        table = TapTable.objects.using('tap').get(pk=instance.table.id)
    except TapTable.DoesNotExist:
        table = None

    if tap and table:
        try:
            column = TapColumn.objects.using('tap').get(pk=instance.id)
            column.table = table
        except TapColumn.DoesNotExist:
            column = TapColumn.objects.using('tap').create(pk=instance.id, table=table)

        column.table_name = str(instance.table)
        column.column_name = instance.name
        column.datatype = instance.datatype
        column.arraysize = instance.size
        column.size = instance.size
        if instance.description:
            schema.description = instance.description[:255]
        column.utype = instance.utype
        column.unit = instance.unit
        column.ucd = instance.ucd
        column.indexed = instance.indexed
        column.principal = instance.principal
        column.std = instance.std
        column.column_index = instance.order
        column.save()
    else:
        # remove the column from the TAP_SCHEMA (if it exists)
        try:
            TapColumn.objects.using('tap').get(pk=instance.id).delete()
        except TapColumn.DoesNotExist:
            pass


@receiver(post_delete, sender=Column)
def column_deleted_handler(sender, **kwargs):

    instance = kwargs['instance']

    # remove the column from the TAP_SCHEMA (if it exists)
    try:
        TapColumn.objects.using('tap').get(pk=instance.id).delete()
    except TapColumn.DoesNotExist:
        pass
