from __future__ import unicode_literals

from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from jsonfield import JSONField


@python_2_unicode_compatible
class Profile(models.Model):

    user = models.OneToOneField(User)
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
        if self.user.first_name and self.user.last_name:
            return self.user.first_name + ' ' + self.user.last_name
        else:
            return self.user.username


@python_2_unicode_compatible
class DetailKey(models.Model):

    TYPE_CHOICES = (
        ('text', 'Text'),
        ('textarea', 'Textarea'),
        ('checkbox', 'Checkbox'),
        ('radio', 'Radio button'),
        ('select', 'Select'),
        ('multiselect', 'Multiselect'),
    )

    key = models.SlugField()
    label = models.CharField(max_length=256)
    data_type = models.CharField(max_length=11, choices=TYPE_CHOICES)
    help_text = models.TextField(blank=True, help_text=_('Enter a help text to be displayed next to the input element'))
    options = JSONField(null=True, blank=True, help_text=_('Enter valid JSON of the form [[key, label], [key, label], ...]'))
    required = models.BooleanField()

    def __str__(self):
        return self.key

    class Meta:
        ordering = ('key',)

        verbose_name = _('DetailKey')
        verbose_name_plural = _('DetailKeys')


def create_profile_for_user(sender, **kwargs):
    user = kwargs['instance']
    if kwargs['created']:
        profile = Profile()
        profile.user = user
        profile.save()

post_save.connect(create_profile_for_user, sender=User)
