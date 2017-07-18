from django.db import models


class QueryJobManager(models.Manager):

    def filter_by_owner(self, user):
        if user.is_anonymous():
            return self.get_queryset().filter(owner=None)
        else:
            return self.get_queryset().filter(owner=user)
