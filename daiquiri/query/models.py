import os
import json

from celery.result import AsyncResult, EagerResult
from celery.task.control import revoke

from django.conf import settings
from django.contrib.auth.models import Group
from django.db import models
from django.db.utils import OperationalError, ProgrammingError
from django.urls import reverse
from django.utils.encoding import python_2_unicode_compatible
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from rest_framework.exceptions import ValidationError

from jsonfield import JSONField

from queryparser.mysql import MySQLQueryProcessor
from queryparser.adql import ADQLQueryTranslator

from daiquiri.core.adapter import get_adapter
from daiquiri.jobs.models import Job

from .managers import QueryJobManager
from .utils import (
    get_default_table_name,
    get_default_queue,
    get_user_database_name,
    get_download_file_name,
    check_permissions
)
from .tasks import run_query, create_download_file


@python_2_unicode_compatible
class QueryJob(Job):

    objects = QueryJobManager()

    database_name = models.CharField(max_length=256)
    table_name = models.CharField(max_length=256)
    queue = models.CharField(max_length=16)

    query_language = models.CharField(max_length=16)
    query = models.TextField()
    native_query = models.TextField(null=True, blank=True)
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

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.phase = self.PHASE_PENDING
            self.job_type = self.JOB_TYPE_QUERY
            self.creation_time = now()

        return super(QueryJob, self).save(*args, **kwargs)

    def clean(self):
        # set the database name
        if not self.database_name:
            self.database_name = get_user_database_name(self.owner)

        # set a default table name
        if not self.table_name:
            self.table_name = get_default_table_name()

        if not self.query_language:
            raise ValidationError({
                 'query_language': [_('This field may not be blank.')]
            })

        if not self.query:
            raise ValidationError({
                 'query': [_('This field may not be blank.')]
            })

        # remove trailing semicolon from the query
        self.query = self.query.strip(';')

        # translate adql -> mysql string
        if self.query_language == 'adql-2.0':
            try:
                translator = ADQLQueryTranslator(self.query)
                self.native_query = translator.to_mysql()
            except RuntimeError as e:
                raise ValidationError({
                     'query': [e.message]
                })
        else:
            self.native_query = self.query

        # parse the query
        processor = MySQLQueryProcessor(self.native_query)
        processor.process_query()

        # check for syntax errors
        if processor.syntax_errors:
            raise ValidationError({
                'query': {
                    'messages': [_('There has been an error while parsing your query.')],
                    'positions': json.dumps(processor.syntax_errors),
                }
            })

        # check permissions
        permission_messages = check_permissions(self.owner, processor.keywords, processor.columns, processor.functions)
        if permission_messages:
            raise ValidationError({
                'query': permission_messages
            })

    @property
    def parameters(self):
        return {
            'database_name': self.database_name,
            'table_name': self.table_name,
            'query_language': self.query_language,
            'query': self.query,
            'native_query': self.native_query,
            'actual_query': self.actual_query,
            'queue': self.queue,
            'nrows': self.nrows,
            'size': self.size
        }

    @property
    def timeout(self):
        if self.queue:
            return (queue['timeout'] for queue in settings.QUERY['queues'] if queue['key'] == self.queue).next()
        else:
            return 10

    @property
    def priority(self):
        return (queue['priority'] for queue in settings.QUERY['queues'] if queue['key'] == self.queue).next()

    @property
    def results(self):
        if self.phase == self.PHASE_COMPLETED:
            # create dictionary of the form
            # 'votable': '/query/api/jobs/{job.id}/stream/votable'
            return {download_format['key']: reverse('query:job-stream', kwargs={
                'pk': str(self.id),
                'format_key': download_format['key']
            }) for download_format in settings.QUERY['download_formats']}
        else:
            return {}

    @property
    def result(self):
        if self.phase == self.PHASE_COMPLETED:
            return reverse('query:job-stream', kwargs={
                'pk': str(self.id),
                'format_key': 'votable'
            })

        else:
            return None

    @property
    def quote(self):
        return None

    @property
    def error(self):
        return None

    def run(self, sync=False):
        if self.phase == self.PHASE_PENDING:
            self.phase = self.PHASE_QUEUED
            self.save()

            # start the submit_query task in a syncronous or asuncronous way
            job_id = str(self.id)
            if not settings.ASYNC or sync:
                run_query.apply((job_id, ), task_id=job_id)

            else:
                if not self.queue:
                    self.queue = get_default_queue()
                    self.save()

                run_query.apply_async((job_id, ), task_id=job_id, queue='query', priority=self.priority)

        else:
            raise ValidationError({
                'phase': ['Job is not PENDING.']
            })

    def abort(self):
        old_phase = self.phase

        self.phase = self.PHASE_ABORTED
        self.save()

        if old_phase == self.PHASE_PENDING:
            pass

        elif old_phase == self.PHASE_QUEUED:
            revoke(str(self.id))

        elif old_phase == self.PHASE_EXECUTING:
            self.abort_query()

        else:
            self.drop_table()
            self.nrows = None
            self.size = None
            self.save()

    def archive(self):
        self.drop_table()
        self.phase = self.PHASE_ARCHIVED
        self.nrows = None
        self.size = None
        self.save()

    def rename_table(self, new_table_name):
        if self.table_name != new_table_name:
            get_adapter().database.rename_table(self.database_name, self.table_name, new_table_name)

    def drop_table(self):
        # drop the corresponding database table, but fail silently
        try:
            get_adapter().database.drop_table(self.database_name, self.table_name)
        except ProgrammingError:
            pass

    def abort_query(self):
        # abort the job on the database
        try:
            get_adapter().database.abort_query(self.pid)
        except OperationalError:
            # the query was probably killed before
            pass

    def download(self, format):
        if self.phase == self.PHASE_COMPLETED:
            task_id = '%s-%s' % (self.id, format['key'])
            file_name = get_download_file_name(self.database_name, self.table_name, self.owner_username, format)
            task_args = (file_name, format['key'], self.database_name, self.table_name, self.metadata)

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
                        task_result = create_download_file.apply_async(task_args, task_id=task_id, queue='download')

            return task_result, file_name

        else:
            raise ValidationError({
                'phase': ['Job is not COMPLETED.']
            })

    def stream(self, format):
        if self.phase == self.PHASE_COMPLETED:
            return get_adapter().download.generate(format['key'], self.database_name, self.table_name, self.metadata)

        else:
            raise ValidationError({
                'phase': ['Job is not COMPLETED.']
            })

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
