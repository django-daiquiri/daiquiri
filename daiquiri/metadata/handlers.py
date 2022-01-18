from django.apps import apps
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import Schema, Table, Column


@receiver(post_save, sender=Schema)
def schema_updated_handler(sender, **kwargs):
    if not kwargs.get('raw'):
        if apps.is_installed('daiquiri.oai'):
            from daiquiri.oai.utils import update_records
            update_records('schema', kwargs['instance'])

        if apps.is_installed('daiquiri.datalink'):
            from daiquiri.datalink.utils import update_links
            update_links('schema', kwargs['instance'])


@receiver(post_delete, sender=Schema)
def schema_deleted_handler(sender, **kwargs):
    if not kwargs.get('raw'):
        if apps.is_installed('daiquiri.oai'):
            from daiquiri.oai.utils import delete_records
            delete_records('schema', kwargs['instance'])

        if apps.is_installed('daiquiri.datalink'):
            from daiquiri.datalink.utils import delete_links
            delete_links('schema', kwargs['instance'])


@receiver(post_save, sender=Table)
def table_updated_handler(sender, **kwargs):
    if not kwargs.get('raw'):
        if apps.is_installed('daiquiri.oai'):
            from daiquiri.oai.utils import update_records
            update_records('table', kwargs['instance'])

        if apps.is_installed('daiquiri.datalink'):
            from daiquiri.datalink.utils import update_links
            update_links('table', kwargs['instance'])


@receiver(post_delete, sender=Table)
def table_deleted_handler(sender, **kwargs):
    if not kwargs.get('raw'):
        if apps.is_installed('daiquiri.oai'):
            from daiquiri.oai.utils import delete_records
            delete_records('table', kwargs['instance'])

        if apps.is_installed('daiquiri.datalink'):
            from daiquiri.datalink.utils import delete_links
            delete_links('table', kwargs['instance'])


@receiver(post_save, sender=Column)
def column_updated_handler(sender, **kwargs):
    cache.delete('processor')
