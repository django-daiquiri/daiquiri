from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from daiquiri.metadata.models import Schema, Table

from .utils import (
    update_records,
    delete_records
)


@receiver(post_save, sender=Schema)
def schema_updated_handler(sender, **kwargs):
    update_records(kwargs['instance'])


@receiver(post_delete, sender=Schema)
def schema_deleted_handler(sender, **kwargs):
    delete_records(kwargs['instance'])


@receiver(post_save, sender=Table)
def table_updated_handler(sender, **kwargs):
    update_records(kwargs['instance'])


@receiver(post_delete, sender=Table)
def table_deleted_handler(sender, **kwargs):
    delete_records(kwargs['instance'])
