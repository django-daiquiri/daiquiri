from django.db import models
from django.contrib.auth.models import Group
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from daiquiri.core.constants import ACCESS_LEVEL_CHOICES
from daiquiri.core.managers import AccessLevelManager


@python_2_unicode_compatible
class Directory(models.Model):

    objects = AccessLevelManager()

    path = models.CharField(
        max_length=256,
        verbose_name=_('Path'),
        help_text=_('Path of the directory.')
    )
    access_level = models.CharField(
        max_length=8, choices=ACCESS_LEVEL_CHOICES,
        verbose_name=_('Access level')
    )
    groups = models.ManyToManyField(
        Group, blank=True,
        verbose_name=_('Groups'),
        help_text=_('The groups which have access to this function.')
    )

    class Meta:
        ordering = ('path', )

        verbose_name = _('Directory')
        verbose_name_plural = _('Directory')

        permissions = (('view_function', 'Can view Directory'),)

    def __str__(self):
        return self.path
