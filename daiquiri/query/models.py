import os
import json
import logging
import six

from collections import OrderedDict

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
from queryparser.exceptions import QueryError, QuerySyntaxError

from daiquiri.core.adapter import get_adapter
from daiquiri.core.constants import ACCESS_LEVEL_CHOICES
from daiquiri.jobs.models import Job

from .managers import QueryJobManager, ExampleManager
from .utils import (
    get_quota,
    get_default_table_name,
    get_default_queue,
    get_tap_schema_name,
    get_user_database_name,
    get_download_file_name,
    get_asterisk_columns,
    check_permissions
)
from .tasks import run_query, create_download_file

logger = logging.getLogger(__name__)


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
            self.creation_time = now()

        return super(QueryJob, self).save(*args, **kwargs)

    def process(self):
        if not self.response_format:
            self.response_format = settings.QUERY_DEFAULT_DOWNLOAD_FORMAT

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

        # check quota
        if QueryJob.objects.get_size(self.owner) > get_quota(self.owner):
            raise ValidationError({
                    'query': [_('Quota is exceeded. Please remove some of your jobs.')]
                })

        # translate adql -> mysql string
        if self.query_language == 'adql-2.0':
            try:
                translator = ADQLQueryTranslator(self.query)
                translated_query = translator.to_mysql()
            except QuerySyntaxError as e:
                raise ValidationError({
                    'query': {
                        'messages': [_('There has been an error while parsing your query.')],
                        'positions': json.dumps(e.syntax_errors),
                    }
                })
            except QueryError as e:
                raise ValidationError({
                    'query': {
                        'messages': e.messages,
                    }
                })

        else:
            translated_query = self.query

        # parse the query
        try:
            processor = MySQLQueryProcessor(translated_query)

            tap_schema_name = get_tap_schema_name()
            if tap_schema_name:
                processor.process_query(replace_schema_name={
                    'TAP_SCHEMA': tap_schema_name
                })
            else:
                processor.process_query()

        except QuerySyntaxError as e:
            raise ValidationError({
                'query': {
                    'messages': [_('There has been an error while parsing your query.')],
                    'positions': json.dumps(e.syntax_errors),
                }
            })
        except QueryError as e:
            raise ValidationError({
                'query': {
                    'messages': e.messages,
                }
            })

        # check permissions
        permission_messages = check_permissions(self.owner, processor.keywords, processor.columns, processor.functions)
        if permission_messages:
            raise ValidationError({
                'query': permission_messages
            })

        # process display_columns to expand *
        display_columns = []
        for display_column in processor.display_columns:
            if display_column[0] == '*':
                display_columns += get_asterisk_columns(display_column)
            else:
                display_columns.append(display_column)

        # check for duplicate columns in display_columns
        display_column_names = [column_name for column_name, column in display_columns]
        seen = set()
        duplicate_columns = []
        for column_name in display_column_names:
            if column_name not in seen:
                seen.add(column_name)
            else:
                duplicate_columns.append(column_name)

        if duplicate_columns:
            raise ValidationError({
                'query': [_('Duplicate column name \'%(column)s\'') % {
                    'column': duplicate_column
                } for duplicate_column in duplicate_columns]
            })

        # initialize metadata and store map of aliases
        self.metadata = {
            'display_columns': OrderedDict(display_columns)
        }

        # get the native query from the processor (without trailing semicolon)
        self.native_query = processor.query.rstrip(';')

        # set clean flag
        self.is_clean = True


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
            return six.next((queue['timeout'] for queue in settings.QUERY_QUEUES if queue['key'] == self.queue))
        else:
            return 10

    @property
    def priority(self):
        return six.next((queue['priority'] for queue in settings.QUERY_QUEUES if queue['key'] == self.queue))

    @property
    def result_status(self):
        return 'OK' if self.max_records is None else 'OVERFLOW'

    @property
    def results(self):
        if self.phase == self.PHASE_COMPLETED:
            # create dictionary of the form
            # 'votable': '/query/api/jobs/{job.id}/stream/votable'
            return {download_format['key']: reverse('query:job-stream', kwargs={
                'pk': str(self.id),
                'format_key': download_format['key']
            }) for download_format in settings.QUERY_DOWNLOAD_FORMATS}
        else:
            return {}

    @property
    def result(self):
        return reverse('query:job-stream', kwargs={
            'pk': str(self.id),
            'format_key': self.response_format
        })

    @property
    def quote(self):
        return None

    @property
    def time_queue(self):
        if self.start_time and self.creation_time:
            return (self.start_time - self.creation_time).total_seconds()
        else:
            return None

    @property
    def time_query(self):
        if self.end_time and self.start_time:
            return (self.end_time - self.start_time).total_seconds()
        else:
            return None

    def run(self, sync=False):
        if not self.is_clean:
            raise Exception('job.process() was not called.')

        if self.phase == self.PHASE_PENDING:
            self.phase = self.PHASE_QUEUED
            self.save()

            # start the submit_query task in a syncronous or asuncronous way
            job_id = str(self.id)
            if not settings.ASYNC or sync:
                logger.info('run_query %s submitted (sync)' % self.id)
                run_query.apply((job_id, ), task_id=job_id, throw=True)

            else:
                if not self.queue:
                    self.queue = get_default_queue()
                    self.save()

                logger.info('run_query %s submitted (async, queue=query, priority=%s)' % (self.id, self.priority))
                run_query.apply_async((job_id, ), task_id=job_id, queue='query', priority=self.priority)

        else:
            raise ValidationError({
                'phase': ['Job is not PENDING.']
            })

    def abort(self):
        if settings.ASYNC:
            # first, revoke the task in celery, regardless the phase
            revoke(str(self.id))

        current_phase = self.phase

        if current_phase in self.PHASE_ACTIVE:
            # next, set the phase to ABORTED
            self.phase = self.PHASE_ABORTED
            self.save()

            # finally, abort query, this will trigger OperationalError in the run_query task
            if current_phase == self.PHASE_EXECUTING:
                self.abort_query()

    def archive(self):
        self.abort()
        self.drop_table()
        self.phase = self.PHASE_ARCHIVED
        self.nrows = None
        self.size = None
        self.save()

    def rename_table(self, new_table_name):
        if self.table_name != new_table_name:
            get_adapter().database.rename_table(self.database_name, self.table_name, new_table_name)

            self.metadata['name'] = new_table_name
            self.save()

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
            file_name = get_download_file_name(self.owner, self.table_name, format)

            task_id = file_name
            task_args = (file_name, format['key'], self.database_name, self.table_name, self.metadata, self.result_status, (self.nrows == 0))

            # create directory if necessary
            try:
                os.mkdir(os.path.dirname(file_name))
            except OSError:
                pass

            if not settings.ASYNC:
                if os.path.isfile(file_name):
                    task_result = EagerResult(task_id, None, 'SUCCESS')
                else:
                    logger.info('create_download_file %s submitted (sync)' % self.id)
                    task_result = create_download_file.apply(task_args, task_id=task_id, throw=True)
            else:
                task_result = AsyncResult(task_id)

                if not os.path.isfile(file_name):
                    # create an empty file to prevent multiple pending tasks
                    open(file_name, 'a').close()

                    if task_result.successful():
                        # somebody or something removed the file. start all over again
                        task_result.forget()

                    logger.info('create_download_file %s submitted (async, queue=download)' % self.id)
                    task_result = create_download_file.apply_async(task_args, task_id=task_id, queue='download')

            return task_result, file_name

        else:
            raise ValidationError({
                'phase': ['Job is not COMPLETED.']
            })

    def stream(self, format):
        if self.phase == self.PHASE_COMPLETED:
            return get_adapter().download.generate(format['key'], self.database_name, self.table_name, self.metadata, self.result_status, (self.nrows == 0))

        else:
            raise ValidationError({
                'phase': ['Job is not COMPLETED.']
            })

@python_2_unicode_compatible
class Example(models.Model):

    objects = ExampleManager()

    order = models.IntegerField(
        null=True, blank=True,
        verbose_name=_('Order'),
        help_text=_('Position in lists.')
    )
    name = models.CharField(
        max_length=256,
        verbose_name=_('Name'),
        help_text=_('Identifier of the example.')
    )
    description = models.TextField(
        null=True, blank=True,
        verbose_name=_('Description'),
        help_text=_('A brief description of the example to be displayed in the user interface.')
    )
    query_language = models.CharField(
        max_length=16,
        verbose_name=_('Query language'),
        help_text=_('The query language for this example.')
    )
    query_string = models.TextField(
        verbose_name=_('Query string'),
        help_text=_('The query string (SQL) for this example.')
    )
    access_level = models.CharField(
        max_length=8, choices=ACCESS_LEVEL_CHOICES,
        verbose_name=_('Access level')
    )
    groups = models.ManyToManyField(
        Group, blank=True,
        verbose_name=_('Groups'),
        help_text=_('The groups which have access to the examples.')
    )

    class Meta:
        ordering = ('order',)

        verbose_name = _('Example')
        verbose_name_plural = _('Examples')

        permissions = (('view_example', 'Can view Example'),)

    def __str__(self):
        return self.name
