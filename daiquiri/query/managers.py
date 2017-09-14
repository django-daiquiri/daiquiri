from django.db import models

from daiquiri.core.managers import AccessLevelManager


class QueryJobManager(models.Manager):

    def filter_by_owner(self, user):
        if not user or user.is_anonymous():
            return self.get_queryset().filter(owner=None)
        else:
            return self.get_queryset().filter(owner=user)

    def get_size(self, user):
        # get the size of all the tables of this user
        return self.filter_by_owner(user).exclude(phase=self.model.PHASE_ARCHIVED).aggregate(models.Sum('size'))['size__sum'] or 0


class ExampleManager(AccessLevelManager):

    pass
