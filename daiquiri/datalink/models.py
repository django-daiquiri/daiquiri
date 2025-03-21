from django.db import models
from django.utils.translation import gettext_lazy as _


class Datalink(models.Model):

    datalink_id = models.BigAutoField(primary_key=True)
    ID = models.CharField(
        max_length=256,
        db_index=True,
        verbose_name=_('Identifier'),
    )
    access_url = models.CharField(
        max_length=256,
        verbose_name=_('Access URL'),
    )
    service_def = models.CharField(
        max_length=80, blank=True,
        verbose_name=_('Service definition'),
    )
    error_message = models.CharField(
        max_length=256, blank=True,
        verbose_name=_('Error message'),
    )
    description = models.CharField(
        max_length=256, blank=True,
        verbose_name=_('Description'),
    )
    semantics = models.CharField(
        max_length=80, db_index=True, blank=True,
        verbose_name=_('Semantics'),
    )
    content_type = models.CharField(
        max_length=80, db_index=True,
        verbose_name=_('Content type'),
    )
    content_length = models.BigIntegerField(
        null=True,
        verbose_name=_('Content length'),
    )

    class Meta:
        db_table = 'datalink'

    def __str__(self):
        return self.ID
