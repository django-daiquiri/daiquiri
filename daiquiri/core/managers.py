from django.db import models

from .constants import ACCESS_LEVEL_INTERNAL, ACCESS_LEVEL_PUBLIC


class AccessLevelQuerySet(models.QuerySet):

    def filter_by_access_level(self, user):
        if not user or user.is_anonymous:
            return self.filter(access_level=ACCESS_LEVEL_PUBLIC)
        else:
            q = models.Q(access_level=ACCESS_LEVEL_PUBLIC) | \
                models.Q(access_level=ACCESS_LEVEL_INTERNAL) | \
                models.Q(groups__in=user.groups.all())
            return self.filter(q).distinct()

    def filter_by_metadata_access_level(self, user):
        if not user or user.is_anonymous:
            return self.filter(metadata_access_level=ACCESS_LEVEL_PUBLIC)
        else:
            q = models.Q(metadata_access_level=ACCESS_LEVEL_PUBLIC) | \
                models.Q(metadata_access_level=ACCESS_LEVEL_INTERNAL) | \
                models.Q(groups__in=user.groups.all())
            return self.filter(q).distinct()


class AccessLevelManager(models.Manager):

    def get_queryset(self):
        return AccessLevelQuerySet(self.model, using=self._db)

    def filter_by_access_level(self, user):
        return self.get_queryset().filter_by_access_level(user)

    def filter_by_metadata_access_level(self, user):
        return self.get_queryset().filter_by_metadata_access_level(user)
