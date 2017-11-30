from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from jsonfield import JSONField


@python_2_unicode_compatible
class Record(models.Model):

    time = models.DateTimeField()

    resource_type = models.CharField(max_length=32)
    resource = JSONField()

    client_ip = models.GenericIPAddressField(blank=True, null=True)
    user = models.ForeignKey(User, blank=True, null=True)

    class Meta:
        ordering = ('-time', )

        verbose_name = _('Record')
        verbose_name_plural = _('Records')

        permissions = (('view_record', 'Can view Record'),)

    def __str__(self):
        return '%s %s' % (self.time, self.resource_type)
