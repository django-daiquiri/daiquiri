from __future__ import unicode_literals


import logging
import uuid

# from django.contrib.auth.models import User
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from jsonfield import JSONField

# from .utils import get_full_name
# from .signals import user_created, user_updated, user_confirmed, user_activated, user_disabled, user_enabled

logger = logging.getLogger(__name__)


@python_2_unicode_compatible
class ContactMessage(models.Model):

    STATUS_CHOICES = (
        ('STATUS_ACTIVE', 'active'),
        ('STATUS_CLOSED', 'closed')
    )

    CATEGORY_CHOICES = (
        ('CATEGORY_SUPPORT', 'Support'),
        ('CATEGORY_BUG', 'Bug')
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    name = models.CharField(max_length=30)
    email = models.CharField(max_length=30)
    subject = models.CharField(max_length=30)

#    User = models.OneToOneField(User)
    category = JSONField(null=True, blank=True)
    status = JSONField(null=True, blank=True)
    datetime = models.DateTimeField(blank=True, null=True)

    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)

    message = models.CharField(max_length=450)

    class Meta:
        ordering = ('datetime',)

        verbose_name = _('Contact message')
        verbose_name_plural = _('Contact messages')

    def __str__(self):
        return self.get_str()

    def get_str(self):
        return "id=%s; category=%s; status=%s" % (str(self.id), self.category, self.status)

    def set_status_closed(self):
        if self.status != STATUS_CLOSED:
            self.status = STATUS_CLOSED
            self.save()

    def set_status_active(self):
        self.status = STATUS_ACTIVE
        self.save()
