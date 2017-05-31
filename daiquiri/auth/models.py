from __future__ import unicode_literals

import logging

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from jsonfield import JSONField

from .utils import get_full_name
from .signals import user_created, user_updated, user_confirmed, user_activated, user_disabled, user_enabled

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
        logger.info('User \'%s\' confirmed by \'%s\'.' % (self.user.username, request.user.username))

    def activate(self, request):
        self.is_confirmed = True
        self.is_pending = False
        self.save()

        user_activated.send(sender=self.__class__, request=request, user=self.user)
        logger.info('User \'%s\' activated by \'%s\'.' % (self.user.username, request.user.username))

    def disable(self, request):
        self.user.is_active = False
        self.user.save()

        user_disabled.send(sender=self.__class__, request=request, user=self.user)
        logger.info('User \'%s\' disabled by \'%s\'.' % (self.user.username, request.user.username))

    def enable(self, request):
        self.user.is_active = True
        self.user.save()

        user_enabled.send(sender=self.__class__, request=request, user=self.user)
        logger.info('User \'%s\' enabled by \'%s\'.' % (self.user.username, request.user.username))


@receiver(post_save, sender=User)
def post_save_user(sender, **kwargs):
    if not kwargs.get('raw', False):
        user = kwargs['instance']

        if kwargs['created']:
            profile = Profile()
            profile.user = user
            profile.save()

            user_created.send(sender=User, user=user)
            logger.info('User \'%s\' created.' % user.username)
        else:
            user_updated.send(sender=User, user=user)
            logger.info('User \'%s\' updated.' % user.username)


@receiver(post_save, sender=Profile)
def post_save_profile(sender, **kwargs):
    if not kwargs.get('raw', False):
        profile = kwargs['instance']

        if not kwargs['created']:
            user_updated.send(sender=Profile, user=profile.user)
            logger.info('User \'%s\' updated.' % profile.user.username)
