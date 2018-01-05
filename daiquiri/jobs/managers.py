from django.db import models


class JobManager(models.Manager):

    def filter_by_owner(self, user):
        if not user or user.is_anonymous():
            return self.get_queryset().filter(owner=None)
        else:
            return self.get_queryset().filter(owner=user)
