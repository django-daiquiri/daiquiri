from django.db import models

from daiquiri.metadata.managers import MetadataManager


class QueryJobManager(models.Manager):

    def filter_by_owner(self, user):
        if user.is_anonymous():
            return self.get_queryset().filter(owner=None)
        else:
            return self.get_queryset().filter(owner=user)

class ExampleManager(MetadataManager):

    pass
