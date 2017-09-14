from django.db import models

from .constants import ACCESS_LEVEL_PUBLIC, ACCESS_LEVEL_INTERNAL


class AccessLevelManager(models.Manager):

    def filter_by_access_level(self, user):
        if not user or user.is_anonymous():
            return self.get_queryset().filter(access_level=ACCESS_LEVEL_PUBLIC)
        else:
            q = models.Q(access_level=ACCESS_LEVEL_PUBLIC) | \
                models.Q(access_level=ACCESS_LEVEL_INTERNAL) | \
                models.Q(groups__in=user.groups.all())
            return self.get_queryset().filter(q)

    def filter_by_metadata_access_level(self, user):
        if not user or user.is_anonymous():
            return self.get_queryset().filter(metadata_access_level=ACCESS_LEVEL_PUBLIC)
        else:
            q = models.Q(metadata_access_level=ACCESS_LEVEL_PUBLIC) | \
                models.Q(metadata_access_level=ACCESS_LEVEL_INTERNAL) | \
                models.Q(groups__in=user.groups.all())
            return self.get_queryset().filter(q)
