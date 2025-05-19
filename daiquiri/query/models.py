import logging
import os
from collections import OrderedDict

from django.conf import settings
from django.contrib.auth.models import Group
from django.db import models
from django.db.utils import DataError, InternalError, OperationalError, ProgrammingError
from django.utils.functional import cached_property
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from daiquiri.core.adapter import DatabaseAdapter, DownloadAdapter
from daiquiri.core.constants import ACCESS_LEVEL_CHOICES
from daiquiri.core.utils import get_date_display
from daiquiri.files.utils import check_file
from daiquiri.jobs.managers import JobManager
from daiquiri.jobs.models import Job
from daiquiri.stats.models import Record

from .managers import ExampleManager, QueryJobManager
from .process import (
    check_number_of_active_jobs,
    check_permissions,
    check_quota,
    process_display_columns,
    process_query,
    process_query_language,
    process_queue,
    process_response_format,
    process_schema_name,
    process_table_name,
    process_user_columns,
    translate_query,
)
from .tasks import (
    abort_database_query_task,
    create_download_archive_task,
    create_download_table_task,
    drop_database_table_task,
    rename_database_table_task,
    run_database_ingest_task,
    run_database_query_task,
)
from .utils import get_format_config, get_job_columns, get_query_language_label

logger = logging.getLogger(__name__)
query_logger = logging.getLogger('query')


class QueryJob(Job):
    objects = QueryJobManager()

    schema_name = models.CharField(max_length=256)
    table_name = models.CharField(max_length=256)
    queue = models.CharField(max_length=16, blank=True)

    query_language = models.CharField(max_length=16, blank=True)
    query = models.TextField(blank=True)
    native_query = models.TextField(blank=True)
    actual_query = models.TextField(blank=True)

    queue = models.CharField(max_length=16, blank=True)
    nrows = models.BigIntegerField(null=True, blank=True)
    size = models.BigIntegerField(null=True, blank=True)

    metadata = models.JSONField(null=True, blank=True)
    uploads = models.JSONField(null=True, blank=True)

    pid = models.IntegerField(null=True, blank=True)

    class Meta:
        ordering = ('start_time',)
        verbose_name = _('QueryJob')
        verbose_name_plural = _('QueryJobs')

    @property
    def phase_label(self):
        return self.get_phase_display()

    @property
    def query_language_label(self):
        return get_query_language_label(self.query_language)

    @property
    def creation_time_label(self):
        return get_date_display(self.creation_time)

    @property
    def start_time_label(self):
        return get_date_display(self.start_time)

    @property
    def end_time_label(self):
        return get_date_display(self.end_time)

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
            'size': self.size,
        }

    @property
    def formats(self):
        return OrderedDict(
            (item['key'], item['content_type'])
            for item in settings.QUERY_DOWNLOAD_FORMATS
        )

    @property
    def result_status(self):
        # if max_records is not defined then any number of rows is valid
        if self.max_records is None or self.nrows is None:
            return 'OK'
        else:
            return 'OK' if self.nrows < self.max_records else 'OVERFLOW'

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
            return next(
                queue['timeout']
                for queue in settings.QUERY_QUEUES
                if queue['key'] == self.queue
            )
        else:
            return 10

    @cached_property
    def column_names(self):
        return [column['name'] for column in self.metadata['columns']]

    def process(self, upload=False):
        # log the query to the query log
        query_logger.info(
            '"%s" %s %s', self.query, self.query_language, self.owner or 'anonymous'
        )

        # check quota and number of active jobs
        check_quota(self)
        check_number_of_active_jobs(self)

        # process schema_name, table_name and response format
        self.schema_name = process_schema_name(self.owner, self.schema_name)
        self.table_name = process_table_name(self.table_name)
        self.response_format = process_response_format(self.response_format)

        if upload:
            self.query = ''
            self.query_language = ''
            self.queue = ''
            self.execution_duration = 0.0

        else:
            self.query_language = process_query_language(
                self.owner, self.query_language
            )
            self.queue = process_queue(self.owner, self.queue)
            self.response_format = process_response_format(self.response_format)

            # set the execution_duration to the queues timeout
            self.execution_duration = self.timeout

            # log the input query to the debug log
            logger.debug('query = "%s"', self.query)

            # translate the query from adql
            translated_query = translate_query(self.query_language, self.query)

            # log the translated query to the debug log
            logger.debug('translated_query = "%s"', translated_query)

            processor = process_query(translated_query)

            # log the processor output to the debug log
            logger.debug('native_query = "%s"', processor.query)
            logger.debug('processor.keywords = %s', processor.keywords)
            logger.debug('processor.tables = %s', processor.tables)
            logger.debug('processor.columns = %s', processor.columns)
            logger.debug('processor.functions = %s', processor.functions)

            # check permissions
            permission_messages = check_permissions(
                self.owner,
                processor.keywords,
                processor.tables,
                processor.columns,
                processor.functions,
            )
            if permission_messages:
                raise ValidationError(
                    {
                        'query': {
                            'messages': permission_messages,
                        }
                    }
                )

            # initialize metadata and store map of aliases
            self.metadata = {
                'display_columns': process_display_columns(processor.display_columns),
                'user_columns': process_user_columns(self, processor.tables),
                'tables': processor.tables,
            }

            # get the native query from the processor (without trailing semicolon)
            self.native_query = processor.query.rstrip(';')

            # set clean flag
            self.is_clean = True

    def run(self):
        if not self.is_clean:
            raise Exception('job.process() was not called.')

        if self.phase == self.PHASE_PENDING:
            self.phase = self.PHASE_QUEUED
            self.save()

            # start the submit_query task in a synchronous or asuncronous way
            job_id = str(self.id)
            if not settings.ASYNC:
                logger.info('job %s submitted (sync)', self.id)
                run_database_query_task.apply((job_id,), task_id=job_id, throw=True)

            else:
                queue = f'query_{self.queue}'
                logger.info('job %s submitted (async, queue=%s)', self.id, queue)
                run_database_query_task.apply_async(
                    (job_id,), task_id=job_id, queue=queue
                )

        else:
            raise ValidationError({'phase': ['Job is not PENDING.']})

    def run_sync(self):
        adapter = DatabaseAdapter()

        adapter.create_user_schema_if_not_exists(self.schema_name)

        self.actual_query = adapter.build_query(
            self.schema_name,
            self.table_name,
            self.native_query,
            settings.QUERY_SYNC_TIMEOUT,
            self.max_records,
        )

        adapter.submit_query(self.actual_query)
        self.nrows = adapter.count_rows(self.schema_name, self.table_name)
        self.size = adapter.fetch_size(self.schema_name, self.table_name)

        # create a stats record for this job
        Record.objects.create(
            time=now(),
            resource_type='QUERY',
            resource={
                'job_id': None,
                'job_type': self.job_type,
            },
            client_ip=self.client_ip,
            user=self.owner,
            size=self.size,
        )

        try:
            yield from DownloadAdapter().generate(
                'votable',
                get_job_columns(self),
                sources=self.metadata.get('sources', []),
                schema_name=self.schema_name,
                table_name=self.table_name,
                nrows=self.nrows,
                query_status=self.result_status,
                query=self.native_query,
                query_language=self.query_language,
            )

            self.drop_uploads()
            self.drop_table()

        except (OperationalError, ProgrammingError, InternalError, DataError) as e:
            raise StopIteration from e

    def ingest(self, file_path):
        if self.phase == self.PHASE_PENDING:
            self.phase = self.PHASE_QUEUED
            self.save()

            if not settings.ASYNC:
                run_database_ingest_task.apply((self.id, file_path), throw=True)
            else:
                run_database_ingest_task.apply_async(
                    (self.id, file_path), queue='download'
                )

        else:
            raise ValidationError({'phase': ['Job is not PENDING.']})

    def abort(self):
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
        self.drop_uploads()
        self.phase = self.PHASE_ARCHIVED
        self.nrows = None
        self.size = None
        self.save()

    def rename_table(self, new_table_name):
        if self.table_name != new_table_name:
            self.metadata['name'] = new_table_name
            self.save()

            task_args = (self.schema_name, self.table_name, new_table_name)

            if not settings.ASYNC:
                rename_database_table_task.apply(task_args, throw=True)
            else:
                rename_database_table_task.apply_async(task_args)

    def drop_table(self):
        task_args = (self.schema_name, self.table_name)

        if not settings.ASYNC:
            drop_database_table_task.apply(task_args, throw=True)
        else:
            drop_database_table_task.apply_async(task_args)

    def drop_uploads(self):
        if self.uploads:
            for table_name, file_path in self.uploads.items():
                task_args = (settings.TAP_UPLOAD, table_name)

                if not settings.ASYNC:
                    drop_database_table_task.apply(task_args, throw=True)
                else:
                    drop_database_table_task.apply_async(task_args)

    def abort_query(self):
        task_args = (self.pid,)

        if not settings.ASYNC:
            abort_database_query_task.apply(task_args, throw=True)
        else:
            abort_database_query_task.apply_async(task_args)

    def stream(self, format_key):
        if self.phase == self.PHASE_COMPLETED:
            return DownloadAdapter().generate(
                format_key,
                self.metadata.get('columns', []),
                sources=self.metadata.get('sources', []),
                schema_name=self.schema_name,
                table_name=self.table_name,
                nrows=self.nrows,
                query_status=self.result_status,
                query=self.query,
                query_language=self.query_language,
            )
        else:
            raise ValidationError({'phase': ['Job is not COMPLETED.']})

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
                count = adapter.count_rows(
                    self.schema_name, self.table_name, column_names, search, filters
                )

                # query the paginated rowset
                rows = adapter.fetch_rows(
                    self.schema_name,
                    self.table_name,
                    column_names,
                    ordering,
                    page,
                    page_size,
                    search,
                    filters,
                )

                # flatten the list if only one column is retrieved
                if len(column_names) == 1:
                    return count, [element for row in rows for element in row]
                else:
                    return count, rows

            except ProgrammingError:
                return 0, []

        else:
            raise ValidationError({'phase': ['Job is not COMPLETED.']})

    def columns(self):
        if self.metadata:
            return self.metadata.get('columns', [])
        else:
            return []


class DownloadJob(Job):
    objects = JobManager()

    query_job = models.ForeignKey(
        QueryJob,
        related_name='downloads',
        on_delete=models.CASCADE,
        verbose_name=_('QueryJob'),
        help_text=_('QueryJob this DownloadJob belongs to.'),
    )
    format_key = models.CharField(
        max_length=32,
        verbose_name=_('Format key'),
        help_text=_('Format key for this download.'),
    )

    class Meta:
        ordering = ('start_time',)

        verbose_name = _('DownloadJob')
        verbose_name_plural = _('DownloadJobs')

    @cached_property
    def file_path(self):
        if not self.owner:
            username = 'anonymous'
        else:
            username = self.owner.username

        format_config = get_format_config(self.format_key)

        if format_config:
            directory_name = os.path.join(settings.QUERY_DOWNLOAD_DIR, username)
            return os.path.join(
                directory_name,
                '{}.{}'.format(self.query_job.table_name, format_config['extension']),
            )
        else:
            return None

    def process(self):
        if self.query_job.phase == self.PHASE_COMPLETED:
            self.owner = self.query_job.owner
        else:
            raise ValidationError({'phase': ['Job is not COMPLETED.']})

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
                logger.info('download_job %s submitted (sync)', download_id)
                create_download_table_task.apply(
                    (download_id,), task_id=download_id, throw=True
                )

            else:
                logger.info(
                    'download_job %s submitted (async, queue=download)', download_id
                )
                create_download_table_task.apply_async(
                    (download_id,), task_id=download_id, queue='download'
                )

        else:
            raise ValidationError({'phase': ['Job is not PENDING.']})

    def delete_file(self):
        try:
            if self.file_path is not None:
                os.remove(self.file_path)
        except OSError:
            pass


class QueryArchiveJob(Job):
    objects = JobManager()

    query_job = models.ForeignKey(
        QueryJob,
        related_name='archives',
        on_delete=models.CASCADE,
        verbose_name=_('QueryJob'),
        help_text=_('QueryJob this ArchiveJob belongs to.'),
    )
    column_name = models.CharField(
        max_length=32,
        verbose_name=_('Column name'),
        help_text=_('Column name for this download.'),
    )
    files = models.JSONField(
        verbose_name=_('Files'),
        help_text=_('List of files in the archive.'),
        default=list,
    )

    class Meta:
        ordering = ('start_time',)

        verbose_name = _('QueryArchiveJob')
        verbose_name_plural = _('QueryArchiveJob')

    @cached_property
    def file_path(self):
        if not self.owner:
            username = 'anonymous'
        else:
            username = self.owner.username

        directory_name = os.path.join(settings.QUERY_DOWNLOAD_DIR, username)
        return os.path.join(
            directory_name, f'{self.query_job.table_name}.{self.column_name}.zip'
        )

    def process(self):
        if self.query_job.phase == self.PHASE_COMPLETED:
            self.owner = self.query_job.owner
        else:
            raise ValidationError({'phase': ['Job is not COMPLETED.']})

        if not self.column_name:
            raise ValidationError({'column_name': [_('This field may not be blank.')]})

        if self.column_name not in self.query_job.column_names:
            raise ValidationError(
                {'column_name': [_('Unknown column "%s".') % self.column_name]}
            )

        # get database adapter and query the paginated rowset
        rows = DatabaseAdapter().fetch_rows(
            self.query_job.schema_name,
            self.query_job.table_name,
            [self.column_name],
            page_size=0,
        )

        # prepare list of files for this job
        files = []
        for row in rows:
            file_path = row[0]

            # append the file to the list of files  if it exists
            if file_path and check_file(self.owner, file_path):
                files.append(file_path)
            else:
                raise ValidationError(
                    {'files': [_('One or more of the files cannot be found.')]}
                )

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
                logger.info('archive_job %s submitted (sync)', archive_id)
                create_download_archive_task.apply(
                    (archive_id,), task_id=archive_id, throw=True
                )

            else:
                logger.info(
                    'archive_job %s submitted (async, queue=download)', archive_id
                )
                create_download_archive_task.apply_async(
                    (archive_id,), task_id=archive_id, queue='download'
                )

        else:
            raise ValidationError({'phase': ['Job is not PENDING.']})

    def delete_file(self):
        try:
            os.remove(self.file_path)
        except OSError:
            pass


class Example(models.Model):
    order = models.IntegerField(
        null=True,
        blank=True,
        verbose_name=_('Order'),
        help_text=_('Position in lists.'),
    )
    name = models.CharField(
        max_length=256,
        verbose_name=_('Name'),
        help_text=_('Identifier of the example.'),
    )
    description = models.TextField(  # noqa: DJ001
        null=True,
        blank=True,
        verbose_name=_('Description'),
        help_text=_(
            'A brief description of the example to be displayed in the user interface.'
        ),
    )
    query_language = models.CharField(
        max_length=16,
        verbose_name=_('Query language'),
        help_text=_('The query language for this example.'),
    )
    query_string = models.TextField(
        verbose_name=_('Query string'),
        help_text=_('The query string (SQL) for this example.'),
    )
    access_level = models.CharField(
        max_length=8, choices=ACCESS_LEVEL_CHOICES, verbose_name=_('Access level')
    )
    groups = models.ManyToManyField(
        Group,
        blank=True,
        verbose_name=_('Groups'),
        help_text=_('The groups which have access to the examples.'),
    )

    objects = ExampleManager()

    class Meta:
        ordering = ('order',)

        verbose_name = _('Example')
        verbose_name_plural = _('Examples')

    def __str__(self):
        return self.name

    @property
    def query_language_label(self):
        return get_query_language_label(self.query_language)
