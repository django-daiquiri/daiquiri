from django.db import models


class JobQuerySet(models.QuerySet):

    def delete(self, *args, **kwargs):
        # drop tables for all deleted jobs
        for job in self.all():
            if hasattr(job, 'queryjob'):
                job.queryjob.drop_table()

        return super(JobQuerySet, self).delete(*args, **kwargs)


class JobManager(models.Manager):

    def get_queryset(self):
        return JobQuerySet(self.model, using=self._db)
