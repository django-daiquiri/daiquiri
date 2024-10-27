from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _

from daiquiri.core.encoders import UUIDJSONEncoder


class Record(models.Model):

    time = models.DateTimeField()

    resource_type = models.CharField(max_length=32)
    resource = models.JSONField(encoder=UUIDJSONEncoder)

    client_ip = models.GenericIPAddressField(blank=True, null=True)
    user = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL)

    size = models.PositiveBigIntegerField(null=True, blank=True)

    class Meta:
        ordering = ('-time', )

        verbose_name = _('Record')
        verbose_name_plural = _('Records')

    def __str__(self):
        return f'{self.time} {self.resource_type}'
