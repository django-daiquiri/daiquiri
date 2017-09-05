from __future__ import unicode_literals

import logging

from django.contrib.auth.models import User
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from jsonfield import JSONField

from .utils import get_full_name
from .signals import (
    user_confirmed,
    user_rejected,
    user_activated,
    user_disabled,
    user_enabled
)

logger = logging.getLogger(__name__)


@python_2_unicode_compatible
class Profile(models.Model):

    user = models.OneToOneField(User)
    is_pending = models.BooleanField(default=False)
    is_confirmed = models.BooleanField(default=False)
    details = JSONField(null=True, blank=True)
    attributes = JSONField(null=True, blank=True)

    class Meta:
        ordering = ('user__last_name', 'user__last_name', 'user__username')

        verbose_name = _('Profile')
        verbose_name_plural = _('Profiles')

        permissions = (('view_profile', 'Can view Profile'),)

    def __str__(self):
        return self.user.username

    @property
    def full_name(self):
        return get_full_name(self.user)

    def confirm(self, request):
        self.is_confirmed = True
        self.save()

        user_confirmed.send(sender=self.__class__, request=request, user=self.user)

    def reject(self, request):
        self.is_pending = False
        self.user.is_active = False
        self.save()

        user_rejected.send(sender=self.__class__, request=request, user=self.user)


    def activate(self, request):
        self.is_confirmed = True
        self.is_pending = False
        self.save()

        user_activated.send(sender=self.__class__, request=request, user=self.user)


    def disable(self, request):
        self.user.is_active = False
        self.user.save(update_fields=['is_active'])

        user_disabled.send(sender=self.__class__, request=request, user=self.user)


    def enable(self, request):
        self.user.is_active = True
        self.user.save(update_fields=['is_active'])

        user_enabled.send(sender=self.__class__, request=request, user=self.user)
