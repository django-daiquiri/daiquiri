from django.db import models
from django.utils.translation import gettext_lazy as _


class Record(models.Model):

    identifier = models.CharField(
        max_length=256,
        db_index=True,
        verbose_name=_('OAI identifier'),
    )
    datestamp = models.DateField(
        db_index=True,
        verbose_name=_('OAI datestamp'),
    )
    metadata_prefix = models.CharField(
        max_length=16, db_index=True,
        verbose_name=_('OAI metadataPrefix'),
    )
    set_spec = models.CharField(
        max_length=256, db_index=True, blank=True,
        verbose_name=_('OAI set spec'),
    )
    deleted = models.BooleanField(
        default=False, db_index=True,
        verbose_name=_('Deleted'),
    )
    resource_type = models.CharField(
        max_length=32, db_index=True,
        verbose_name=_('Resource type'),
    )
    resource_id = models.CharField(
        max_length=256, db_index=True, blank=True,
        verbose_name=_('Resource id'),
    )

    class Meta:
        db_table = 'records'

        ordering = ('-datestamp', )

        verbose_name = _('Record')
        verbose_name_plural = _('Records')

    def __str__(self):
        return self.identifier
