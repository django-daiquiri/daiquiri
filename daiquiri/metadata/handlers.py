from django.core.cache import cache
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Column

@receiver(post_save, sender=Column)
def column_updated_handler(sender, **kwargs):
    cache.delete('processor')
