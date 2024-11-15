from django.db import models

from daiquiri.core.managers import AccessLevelManager
from daiquiri.jobs.managers import JobManager


class QueryJobManager(JobManager):

    def get_size(self, user):
        # get the size of all the tables of this user
        return self.filter_by_owner(user).exclude(phase=self.model.PHASE_ARCHIVED) \
                                         .aggregate(models.Sum('size'))['size__sum'] or 0


class ExampleManager(AccessLevelManager):

    pass
