from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from daiquiri_jobs.models import Job

from .managers import QueryJobsSubmissionManager


@python_2_unicode_compatible
class QueryJob(Job):

    submission = QueryJobsSubmissionManager()

    tablename = models.CharField(max_length=256)
    query = models.TextField()
    queue = models.CharField(max_length=16)
    nrows = models.IntegerField(null=True, blank=True)
    size = models.IntegerField(null=True, blank=True)

    class Meta:
        verbose_name = _('QueryJob')
        verbose_name_plural = _('QueryJobs')

        permissions = (('view_queryjob', 'Can view QueryJob'),)

    def __str__(self):
        return super(QueryJob, self).__str__()
