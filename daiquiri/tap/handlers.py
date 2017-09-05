from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from daiquiri.metadata.models import Database, Table, Column

from .utils import (
    update_database,
    delete_database,
    update_table,
    delete_table,
    update_column,
    delete_column
)

@receiver(post_save, sender=Database)
def database_updated_handler(sender, **kwargs):
    update_database(kwargs['instance'])


@receiver(post_delete, sender=Database)
def database_deleted_handler(sender, **kwargs):
    delete_database(kwargs['instance'])


@receiver(post_save, sender=Table)
def table_updated_handler(sender, **kwargs):
    update_table(kwargs['instance'])


@receiver(post_delete, sender=Table)
def table_deleted_handler(sender, **kwargs):
    delete_table(kwargs['instance'])


@receiver(post_save, sender=Column)
def column_updated_handler(sender, **kwargs):
    update_column(kwargs['instance'])


@receiver(post_delete, sender=Column)
def column_deleted_handler(sender, **kwargs):
    delete_column(kwargs['instance'])
