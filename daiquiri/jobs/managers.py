import hashlib

from django.db import models


class JobManager(models.Manager):

    def filter_by_owner(self, user):
        if not user or user.is_anonymous:
            return self.get_queryset().filter(owner=None)
        else:
            return self.get_queryset().filter(owner=user)

    def get_active(self, user):
        # get the number of PENDING, QUEUED or EXECUTING jobs
        return self.filter_by_owner(user).filter(phase__in=self.model.PHASE_ACTIVE)

    def get_hash(self, user):
        jobs = self.filter_by_owner(user)\
                .exclude(phase=self.model.PHASE_ARCHIVED)\
                .order_by('creation_time')\
                .values('id', 'phase')
        jobs_string = '\n'.join(['{id}-{phase}'.format(**job) for job in jobs])
        return hashlib.sha256(jobs_string.encode()).hexdigest()
