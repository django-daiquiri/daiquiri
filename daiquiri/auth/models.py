import logging

from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .signals import user_activated, user_confirmed, user_disabled, user_enabled, user_rejected
from .utils import get_full_name

logger = logging.getLogger(__name__)


class Profile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    is_pending = models.BooleanField(
        default=False,
        help_text='Designates whether the user waiting on confirmation by a manager.')
    is_confirmed = models.BooleanField(
        default=False,
        help_text='Designates whether the user was confirmed by a manager.')
    details = models.JSONField(null=True, blank=True)
    attributes = models.JSONField(null=True, blank=True)
    consent = models.BooleanField(
        default=False,
        help_text='Designates whether the user has agreed to the terms of use.',
        verbose_name='Consent'
    )

    class Meta:
        ordering = ('user__last_name', 'user__last_name', 'user__username')

        verbose_name = _('Profile')
        verbose_name_plural = _('Profiles')

    def __str__(self):
        return self.user.username

    @property
    def full_name(self):
        return get_full_name(self.user)

    def user_admin_url(self):
        return reverse('admin:auth_user_change', args=[self.user.id])

    def profile_admin_url(self):
        return reverse('admin:daiquiri_auth_profile_change', args=[self.id])

    def confirm(self, request):
        self.is_confirmed = True
        self.save()

        user_confirmed.send(sender=self.__class__, request=request, user=self.user)

    def reject(self, request):
        self.is_pending = False
        self.user.is_active = False
        self.user.save(update_fields=['is_active'])
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
