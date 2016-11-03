from django.conf import settings
from django.db import models
from django.db.utils import OperationalError
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from daiquiri_core.adapter import get_adapter
from daiquiri_jobs.models import Job

from .managers import QueryJobManager
from .exceptions import *


@python_2_unicode_compatible
class QueryJob(Job):

    objects = QueryJobManager()

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

    @property
    def parameters(self):
        return {
            'database_name': self.database_name,
            'table_name': self.table_name,
            'queue': self.queue,
            'query_language': self.query_language,
            'query': self.query,
            'actual_query': self.actual_query,
            'queue': self.queue,
            'nrows': self.nrows,
            'size': self.size
        }

    def rename_table(self, new_table_name):
        if self.table_name != new_table_name:
            try:
                adapter = get_adapter('data')
                # self.table is still the old name since Job is updated first
                adapter.rename_table(self.database_name, self.table_name, new_table_name)
            except OperationalError as e:
                raise TableError(e.args[1])

    def drop_table(self):
        adapter = get_adapter('data')
        adapter.drop_table(self.database_name, self.table_name)

        self.nrows = None
        self.size = None
        self.save()
