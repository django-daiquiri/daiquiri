from django.conf import settings
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from daiquiri_jobs.models import Job

from .managers import QueryJobsSubmissionManager


@python_2_unicode_compatible
class QueryJob(Job):

    objects = models.Manager()
    submission = QueryJobsSubmissionManager()

    database_name = models.CharField(max_length=256)
    table_name = models.CharField(max_length=256)
    queue = models.CharField(max_length=16, choices=settings.QUERY['queues'])

    query_language = models.CharField(max_length=8, choices=settings.QUERY['query_languages'])
    query = models.TextField()
    actual_query = models.TextField(null=True, blank=True)

    queue = models.CharField(max_length=16, choices=settings.QUERY['queues'])
    nrows = models.IntegerField(null=True, blank=True)
    size = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ('start_time', )

        verbose_name = _('QueryJob')
        verbose_name_plural = _('QueryJobs')

        permissions = (('view_queryjob', 'Can view QueryJob'),)

    def __str__(self):
        return self.get_str()
