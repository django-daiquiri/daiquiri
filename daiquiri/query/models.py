import os

from celery.result import AsyncResult, EagerResult
from celery.task.control import revoke

from django.conf import settings
from django.contrib.auth.models import Group
from django.db import models
from django.db.utils import OperationalError, ProgrammingError
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from jsonfield import JSONField

from daiquiri.core.adapter import get_adapter
from daiquiri.jobs.models import Job
from daiquiri.uws.settings import PHASE_QUEUED, PHASE_EXECUTING, PHASE_COMPLETED, PHASE_ABORTED

from .managers import QueryJobManager
from .exceptions import TableError
from .utils import get_download_file_name
from .tasks import create_download_file


@python_2_unicode_compatible
class QueryJob(Job):

    objects = QueryJobManager()

    database_name = models.CharField(max_length=256)
    table_name = models.CharField(max_length=256)
    queue = models.CharField(max_length=16)

    query_language = models.CharField(max_length=8)
    query = models.TextField()
    actual_query = models.TextField(null=True, blank=True)

    queue = models.CharField(max_length=16, null=True, blank=True)
    nrows = models.IntegerField(null=True, blank=True)
    size = models.IntegerField(null=True, blank=True)

    metadata = JSONField()

    pid = models.IntegerField(null=True, blank=True)

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
                # self.table is still the old name since Job is updated first
                get_adapter().database.rename_table(self.database_name, self.table_name, new_table_name)
            except OperationalError as e:
                raise TableError(e.args[1])

    def drop_table(self):
        # drop the corresponding database table, but fail silently
        if self.phase == PHASE_COMPLETED:
            try:
                get_adapter().database.drop_table(self.database_name, self.table_name)
            except ProgrammingError:
                pass

        self.nrows = None
        self.size = None
        self.save()

    def kill(self):
        phase = self.phase

        self.phase = PHASE_ABORTED
        self.save()

        if phase == PHASE_QUEUED:
            revoke(str(self.id))

        elif phase == PHASE_EXECUTING:
            # kill the job on the database
            try:
                get_adapter().database.kill_query(self.pid)
            except OperationalError:
                # the query was probably killed before
                pass

    def download(self, format):
        task_id = '%s-%s' % (self.id, format['key'])
        file_name = get_download_file_name(self.database_name, self.table_name, self.owner_username, format)
        task_args = (self.database_name, self.table_name, file_name, format['key'])

        try:
            os.mkdir(os.path.dirname(file_name))
        except OSError:
            pass

        if not settings.ASYNC:
            if os.path.isfile(file_name):
                task_result = EagerResult(task_id, None, 'SUCCESS')
            else:
                task_result = create_download_file.apply(task_args, task_id=task_id)
        else:
            task_result = AsyncResult(task_id)

            if not os.path.isfile(file_name):
                if task_result.successful():
                    # somebody or something removed the file. start all over again
                    task_result.forget()
                    task_result = create_download_file.apply_async(task_args, task_id=task_id)

                else:
                    task_result = create_download_file.apply_async(task_args, task_id=task_id)

        return task_result, file_name

    def stream(self, format):
        return get_adapter().download.stream_table_csv(self.database_name, self.table_name)


@python_2_unicode_compatible
class Example(models.Model):

    order = models.IntegerField(null=True, blank=True)

    name = models.CharField(max_length=256)
    description = models.TextField(null=True, blank=True)

    query_string = models.TextField()

    groups = models.ManyToManyField(Group, blank=True)

    class Meta:
        ordering = ('order',)

        verbose_name = _('Example')
        verbose_name_plural = _('Examples')

        permissions = (('view_example', 'Can view Example'),)

    def __str__(self):
        return self.name
