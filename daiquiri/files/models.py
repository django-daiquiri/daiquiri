import os

from django.conf import settings
from django.contrib.auth.models import Group
from django.db import models
from django.utils.translation import gettext_lazy as _

from daiquiri.core.constants import ACCESS_LEVEL_CHOICES
from daiquiri.core.managers import AccessLevelManager


class Directory(models.Model):

    path = models.CharField(
        max_length=256, blank=True,
        verbose_name=_('Path'),
        help_text=_('Path of the directory.')
    )
    layout = models.BooleanField(
        verbose_name=_('Layout'), default=True,
        help_text=_('Use the page layout with the content.')
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
    depth = models.IntegerField(default=0)

    objects = AccessLevelManager()

    class Meta:
        ordering = ('path', )

        verbose_name = _('Directory')
        verbose_name_plural = _('Directory')

    def __str__(self):
        return self.absolute_path

    def save(self):
        self.depth = len(os.path.normpath(self.path).split(os.path.sep))
        super().save()

    @property
    def absolute_path(self):
        return os.path.normpath(os.path.join(settings.FILES_BASE_PATH, os.path.normpath(self.path)))
