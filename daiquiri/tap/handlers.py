from django.dispatch import receiver
from django.db.models.signals import post_save

from daiquiri.metadata.models import Database, Table, Column

from .models import (
    Schema as TapSchema,
    Table as TapTable,
    Column as TapColumn
)


@receiver(post_save, sender=Database)
def database_updated_handler(sender, **kwargs):

    instance = kwargs['instance']

    try:
        schema = TapSchema.objects.using('tap').get(pk=instance.id)
    except TapSchema.DoesNotExist:
        schema = TapSchema(pk=instance.id)

    schema.schema_name = instance.name
    schema.utype = None
    if instance.description:
        schema.description = instance.description[:255]
    schema.save()


@receiver(post_save, sender=Table)
def table_updated_handler(sender, **kwargs):

    instance = kwargs['instance']

    try:
        table = TapTable.objects.using('tap').get(pk=instance.id)
    except TapTable.DoesNotExist:
        table = TapTable(pk=instance.id)

    table.schema = TapSchema.objects.using('tap').get(pk=instance.database.id)
    table.schema_name = str(instance.database)
    table.table_name = instance.name
    table.table_type = instance.type
    table.utype = instance.utype
    if instance.description:
        table.description = instance.description[:255]
    table.table_index = instance.order

    table.save()


@receiver(post_save, sender=Column)
def column_updated_handler(sender, **kwargs):

    instance = kwargs['instance']

    try:
        column = TapColumn.objects.using('tap').get(pk=instance.id)
    except TapColumn.DoesNotExist:
        column = TapColumn(pk=instance.id)

    column.table = TapTable.objects.using('tap').get(pk=instance.table.id)
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
