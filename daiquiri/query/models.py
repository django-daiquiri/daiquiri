import json
import logging
import os
import six

from collections import OrderedDict

from celery.task.control import revoke

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.cache import cache
from django.db import models
from django.db.utils import OperationalError, ProgrammingError
from django.urls import reverse
from django.utils.encoding import python_2_unicode_compatible
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from rest_framework.exceptions import ValidationError

from jsonfield import JSONField

from queryparser.mysql import MySQLQueryProcessor
from queryparser.postgresql import PostgreSQLQueryProcessor
from queryparser.adql import ADQLQueryTranslator
from queryparser.exceptions import QueryError, QuerySyntaxError

from daiquiri.core.adapter import DatabaseAdapter, DownloadAdapter
from daiquiri.core.constants import ACCESS_LEVEL_CHOICES
from daiquiri.jobs.models import Job
from daiquiri.jobs.managers import JobManager
from daiquiri.files.utils import check_file, search_file

from .managers import QueryJobManager, ExampleManager
from .utils import (
    get_quota,
    get_max_active_jobs,
    get_default_table_name,
    get_format_config,
    get_user_schema_name,
    get_asterisk_columns,
    get_indexed_objects,
    check_permissions
)
from .process import (
    process_schema_name,
    process_table_name,
    process_query_language,
    process_queue,
    process_response_format
)
from .tasks import run_query, create_download_file, create_archive_file

logger = logging.getLogger(__name__)


class QueryJob(Job):

    objects = QueryJobManager()

    schema_name = models.CharField(max_length=256)
    table_name = models.CharField(max_length=256)
    queue = models.CharField(max_length=16)

    query_language = models.CharField(max_length=16)
    query = models.TextField()
    native_query = models.TextField(null=True, blank=True)
    actual_query = models.TextField(null=True, blank=True)

    queue = models.CharField(max_length=16, null=True, blank=True)
    nrows = models.BigIntegerField(null=True, blank=True)
    size = models.BigIntegerField(null=True, blank=True)

    metadata = JSONField(blank=True)

    pid = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ('start_time', )

        verbose_name = _('QueryJob')
        verbose_name_plural = _('QueryJobs')

        permissions = (('view_queryjob', 'Can view QueryJob'),)

    @property
    def parameters(self):
        return {
            'schema_name': self.schema_name,
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
    def formats(self):
        return {item['key']: item['content_type'] for item in settings.QUERY_DOWNLOAD_FORMATS}

    @property
    def result_status(self):
        return 'OK' if self.max_records is None else 'OVERFLOW'

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

    @property
    def timeout(self):
        if self.queue:
            return six.next((queue['timeout'] for queue in settings.QUERY_QUEUES if queue['key'] == self.queue))
        else:
            return 10

    @property
    def priority(self):
        return six.next((queue['priority'] for queue in settings.QUERY_QUEUES if queue['key'] == self.queue))

    @cached_property
    def column_names(self):
        return [column['name'] for column in self.metadata['columns']]

    def process(self):

        # process all the things!
        self.schema_name = process_schema_name(self.schema_name, self.owner)
        self.table_name = process_table_name(self.table_name)
        self.query_language = process_query_language(self.query_language)
        self.queue = process_queue(self.queue)
        self.response_format = process_response_format(self.response_format)

        # set the execution_duration to the queues timeout
        self.execution_duration = self.timeout

        # check quota
        if QueryJob.objects.get_size(self.owner) > get_quota(self.owner):
            raise ValidationError({
                'query': [_('Quota is exceeded. Please remove some of your jobs.')]
            })

        # check number of active jobs
        max_active_jobs = get_max_active_jobs(self.owner)
        if max_active_jobs and max_active_jobs <= QueryJob.objects.get_active(self.owner).count():
            raise ValidationError({
                'query': [_('Too many active jobs. Please abort some of your active jobs or wait until they are completed.')]
            })

        # get the adapter
        adapter = DatabaseAdapter()

        # log the input query
        logger.debug('query = "%s"', self.query)

        # translate adql -> mysql string
        if self.query_language == 'adql-2.0':
            try:
                translator = cache.get_or_set('translator', ADQLQueryTranslator(), 3600)
                translator.set_query(self.query)

                if adapter.database_config['ENGINE'] == 'django.db.backends.mysql':
                    translated_query = translator.to_mysql()
                elif adapter.database_config['ENGINE'] == 'django.db.backends.postgresql':
                    translated_query = translator.to_postgresql()
                else:
                    raise Exception('Unknown database engine')

            except QuerySyntaxError as e:
                raise ValidationError({
                    'query': {
                        'messages': [_('There has been an error while translating your query.')],
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

        # log the translated query
        logger.debug('translated_query = "%s"', translated_query)

        # parse the query
        try:
            if adapter.database_config['ENGINE'] == 'django.db.backends.mysql':
                processor = MySQLQueryProcessor(translated_query)
            elif adapter.database_config['ENGINE'] == 'django.db.backends.postgresql':

                processor = cache.get_or_set('processor', PostgreSQLQueryProcessor(indexed_objects=get_indexed_objects()), 3600)
                processor.set_query(translated_query)
                processor.process_query()
            else:
                raise Exception('Unknown database engine')

            processor.process_query(replace_schema_name={
                'TAP_SCHEMA': settings.TAP_SCHEMA
            })

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

        # log the native query
        logger.debug('native_query = "%s"', processor.query)

        # log the processor output
        logger.debug('processor.keywords = %s', processor.keywords)
        logger.debug('processor.tables = %s', processor.tables)
        logger.debug('processor.columns = %s', processor.columns)
        logger.debug('processor.functions = %s', processor.functions)

        # check permissions
        permission_messages = check_permissions(self.owner, processor.keywords, processor.tables, processor.columns, processor.functions)
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
            'display_columns': OrderedDict(display_columns),
            'tables': processor.tables
        }

        # get the native query from the processor (without trailing semicolon)
        self.native_query = processor.query.rstrip(';')

        # set clean flag
        self.is_clean = True

    def run(self, sync=False):
        if not self.is_clean:
            raise Exception('job.process() was not called.')

        if self.phase == self.PHASE_PENDING:
            self.phase = self.PHASE_QUEUED
            self.save()

            # start the submit_query task in a syncronous or asuncronous way
            job_id = str(self.id)
            if not settings.ASYNC or sync:
                logger.info('job %s submitted (sync)' % self.id)
                run_query.apply((job_id, ), task_id=job_id, throw=True)

            else:
                logger.info('job %s submitted (async, queue=query, priority=%s)' % (self.id, self.priority))
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
            DatabaseAdapter().rename_table(self.schema_name, self.table_name, new_table_name)

            self.metadata['name'] = new_table_name
            self.save()

    def drop_table(self):
        # drop the corresponding database table, but fail silently
        try:
            DatabaseAdapter().drop_table(self.schema_name, self.table_name)
        except ProgrammingError:
            pass

    def abort_query(self):
        # abort the job on the database
        try:
            DatabaseAdapter().abort_query(self.pid)
        except OperationalError:
            # the query was probably killed before
            pass

    def stream(self, format_key):
        if self.phase == self.PHASE_COMPLETED:
            return DownloadAdapter().generate(
                format_key,
                self.schema_name,
                self.table_name,
                self.metadata.get('columns'),
                self.metadata.get('sources'),
                self.result_status,
                (self.nrows == 0)
            )
        else:
            raise ValidationError({
                'phase': ['Job is not COMPLETED.']
            })

    def rows(self, column_names, ordering, page, page_size, search, filters):
        if self.phase == self.PHASE_COMPLETED:
            # check if the columns are actually in the jobs table
            errors = {}

            for column_name in column_names:
                if column_name not in self.column_names:
                    errors[column_name] = _('Column not found.')

            if errors:
                raise ValidationError(errors)

            # get database adapter
            adapter = DatabaseAdapter()

            try:
                # query the database for the total number of rows
                count = adapter.count_rows(self.schema_name, self.table_name, column_names, search, filters)

                # query the paginated rowset
                rows = adapter.fetch_rows(self.schema_name, self.table_name, column_names, ordering, page, page_size, search, filters)

                # flatten the list if only one column is retrieved
                if len(column_names) == 1:
                    return count, [element for row in rows for element in row]
                else:
                    return count, rows

            except ProgrammingError:
                return 0, []

        else:
            raise ValidationError({
                'phase': ['Job is not COMPLETED.']
            })

    def columns(self):
        if self.metadata:
            return self.metadata.get('columns', [])
        else:
            return []


class DownloadJob(Job):

    objects = JobManager()

    job = models.ForeignKey(
        QueryJob, related_name='downloads',
        verbose_name=_('QueryJob'),
        help_text=_('QueryJob this DownloadJob belongs to.')
    )
    format_key = models.CharField(
        max_length=32,
        verbose_name=_('Format key'),
        help_text=_('Format key for this download.')
    )

    class Meta:
        ordering = ('start_time', )

        verbose_name = _('DownloadJob')
        verbose_name_plural = _('DownloadJobs')

        permissions = (('view_downloadjob', 'Can view DownloadJob'),)

    @property
    def file_path(self):
        if not self.owner:
            username = 'anonymous'
        else:
            username = self.owner.username

        format_config = get_format_config(self.format_key)

        if format_config:
            directory_name = os.path.join(settings.QUERY_DOWNLOAD_DIR, username)
            return os.path.join(directory_name, '%s.%s' % (self.job.table_name, format_config['extension']))
        else:
            return None

    def process(self):
        if self.job.phase == self.PHASE_COMPLETED:
            self.owner = self.job.owner
        else:
            raise ValidationError({
                'phase': ['Job is not COMPLETED.']
            })

        # set clean flag
        self.is_clean = True

    def run(self):
        if not self.is_clean:
            raise Exception('download_job.process() was not called.')

        if self.phase == self.PHASE_PENDING:
            self.phase = self.PHASE_QUEUED
            self.save()

            download_id = str(self.id)
            if not settings.ASYNC:
                logger.info('download_job %s submitted (sync)' % download_id)
                create_download_file.apply((download_id, ), task_id=download_id, throw=True)

            else:
                logger.info('download_job %s submitted (async, queue=download)' % download_id)
                create_download_file.apply_async((download_id, ), task_id=download_id, queue='download')

        else:
            raise ValidationError({
                'phase': ['Job is not PENDING.']
            })

    def delete_file(self):
        try:
            if self.file_path is not None:
                os.remove(self.file_path)
        except OSError:
            pass


class QueryArchiveJob(Job):

    objects = JobManager()

    job = models.ForeignKey(
        QueryJob, related_name='archives',
        verbose_name=_('QueryJob'),
        help_text=_('QueryJob this ArchiveJob belongs to.')
    )
    column_name = models.CharField(
        max_length=32,
        verbose_name=_('Column name'),
        help_text=_('Column name for this download.')
    )
    files = JSONField(
        verbose_name=_('Files'),
        help_text=_('List of files in the archive.')
    )

    class Meta:
        ordering = ('start_time', )

        verbose_name = _('QueryArchiveJob')
        verbose_name_plural = _('QueryArchiveJob')

        permissions = (('view_queryarchivejob', 'Can view QueryArchiveJob'),)

    @property
    def file_path(self):
        if not self.owner:
            username = 'anonymous'
        else:
            username = self.owner.username

        directory_name = os.path.join(settings.QUERY_DOWNLOAD_DIR, username)
        return os.path.join(directory_name, '%s.%s.zip' % (self.job.table_name, self.column_name))

    def process(self):
        try:
            get_format_config(self.format_key)
        except IndexError:
            raise ValidationError({'format_key': "Not supported."})

        if self.job.phase == self.PHASE_COMPLETED:
            self.owner = self.job.owner
        else:
            raise ValidationError({
                'phase': ['Job is not COMPLETED.']
            })

        if not self.column_name:
            raise ValidationError({
                'column_name': [_('This field may not be blank.')]
            })

        if self.column_name not in self.job.column_names:
            raise ValidationError({
                'column_name': [_('Unknown column "%s".') % self.column_name]
            })

        # get database adapter and query the paginated rowset
        rows = DatabaseAdapter().fetch_rows(self.job.schema_name, self.job.table_name, [self.column_name], page_size=0)

        # prepare list of files for this job
        files = []

        for row in rows:
            file_path = search_file(row[0])

            # append the file to the list of files  if it exists
            if file_path and check_file(self.owner, file_path):
                files.append(file_path)
            else:
                raise ValidationError({
                    'files': [_('One or more of the files cannot be found.')]
                })

        # set files for this job
        self.files = files

        # set clean flag
        self.is_clean = True

    def run(self):
        if not self.is_clean:
            raise Exception('download_job.process() was not called.')

        if self.phase == self.PHASE_PENDING:
            self.phase = self.PHASE_QUEUED
            self.save()

            archive_id = str(self.id)
            if not settings.ASYNC:
                logger.info('archive_job %s submitted (sync)' % archive_id)
                create_archive_file.apply((archive_id, ), task_id=archive_id, throw=True)

            else:
                logger.info('archive_job %s submitted (async, queue=download)' % archive_id)
                create_archive_file.apply_async((archive_id, ), task_id=archive_id, queue='download')

        else:
            raise ValidationError({
                'phase': ['Job is not PENDING.']
            })

    def delete_file(self):
        try:
            os.remove(self.file_path)
        except OSError:
            pass


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
