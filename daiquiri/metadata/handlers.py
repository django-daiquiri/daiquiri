from django.apps import apps
from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Column, Schema, Table


@receiver(post_save, sender=Schema)
def schema_updated_handler(sender, **kwargs):
    if not kwargs.get('raw'):
        if apps.is_installed('daiquiri.oai'):
            from daiquiri.oai.utils import update_records
            update_records('schema', kwargs['instance'])

        if apps.is_installed('daiquiri.datalink'):
            from daiquiri.datalink.utils import update_links
            update_links('schema', kwargs['instance'])

        if apps.is_installed('daiquiri.tap'):
            from daiquiri.tap.utils import update_schema
            update_schema(kwargs['instance'])


@receiver(post_delete, sender=Schema)
def schema_deleted_handler(sender, **kwargs):
    if not kwargs.get('raw'):
        if apps.is_installed('daiquiri.oai'):
            from daiquiri.oai.utils import delete_records
            delete_records('schema', kwargs['instance'])

        if apps.is_installed('daiquiri.datalink'):
            from daiquiri.datalink.utils import delete_links
            delete_links('schema', kwargs['instance'])

        if apps.is_installed('daiquiri.tap'):
            from daiquiri.tap.utils import delete_schema
            delete_schema(kwargs['instance'])


@receiver(post_save, sender=Table)
def table_updated_handler(sender, **kwargs):
    table = kwargs['instance']

    if not kwargs.get('raw'):
        if apps.is_installed('daiquiri.oai'):
            from daiquiri.oai.utils import update_records
            update_records('table', table)

        if apps.is_installed('daiquiri.datalink'):
            from daiquiri.datalink.utils import update_links
            update_links('table', table)

        if apps.is_installed('daiquiri.tap'):
            from daiquiri.tap.utils import update_table
            update_table(table)


@receiver(post_delete, sender=Table)
def table_deleted_handler(sender, **kwargs):
    table = kwargs['instance']

    if not kwargs.get('raw'):
        if apps.is_installed('daiquiri.oai'):
            from daiquiri.oai.utils import delete_records
            delete_records('table', table)

        if apps.is_installed('daiquiri.datalink'):
            from daiquiri.datalink.utils import delete_links
            delete_links('table', table)

        if apps.is_installed('daiquiri.tap'):
            from daiquiri.tap.utils import delete_table
            delete_table(table)


@receiver(post_save, sender=Column)
def column_updated_handler(sender, **kwargs):
    column = kwargs['instance']

    # clear cached queryparser
    cache.delete('processor')

    if not kwargs.get('raw'):
        if apps.is_installed('daiquiri.tap'):
            from daiquiri.tap.utils import update_column
            update_column(column)


@receiver(post_delete, sender=Column)
def column_deleted_handler(sender, **kwargs):
    column = kwargs['instance']

    if not kwargs.get('raw'):
        if apps.is_installed('daiquiri.tap'):
            from daiquiri.tap.utils import delete_column
            delete_column(column)
