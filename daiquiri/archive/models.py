import logging
import os
import six
import uuid

from django.conf import settings
from django.contrib.auth.models import Group
from django.db import models
from django.http.request import QueryDict
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from rest_framework.exceptions import ValidationError

from jsonfield import JSONField

from daiquiri.core.constants import ACCESS_LEVEL_CHOICES
from daiquiri.core.managers import AccessLevelManager
from daiquiri.core.adapter import DatabaseAdapter
from daiquiri.jobs.models import Job
from daiquiri.jobs.managers import JobManager

from .tasks import create_archive_zip_file

logger = logging.getLogger(__name__)


@python_2_unicode_compatible
class Collection(models.Model):

    objects = AccessLevelManager()

    name = models.CharField(
        max_length=32,
        verbose_name=_('Name'),
        help_text=_('Name of the collection.')
    )
    access_level = models.CharField(
        max_length=8, choices=ACCESS_LEVEL_CHOICES,
        verbose_name=_('Access level')
    )
    groups = models.ManyToManyField(
        Group, blank=True,
        verbose_name=_('Groups'),
        help_text=_('The groups which have access to this function.')
    )

    class Meta:
        ordering = ('name', )

        verbose_name = _('Collection')
        verbose_name_plural = _('Collections')

        permissions = (('view_collection', 'Can view Collection'),)

    def __str__(self):
        return self.name


class ArchiveJob(Job):

    objects = JobManager()

    data = JSONField(
        verbose_name=_('Data'),
        help_text=_('Input data for archive creation.')
    )
    files = JSONField(
        verbose_name=_('Files'),
        help_text=_('List of files in the archive.')
    )

    class Meta:
        ordering = ('start_time', )

        verbose_name = _('ArchiveJob')
        verbose_name_plural = _('ArchiveJobs')

        permissions = (('view_archivejob', 'Can view ArchiveJob'),)


    @property
    def file_path(self):
        if not self.owner:
            username = 'anonymous'
        else:
            username = self.owner.username

        directory_name = os.path.join(settings.ARCHIVE_DOWNLOAD_DIR, username)
        return os.path.join(directory_name, str(self.id) + '.zip')

    def process(self):
        # get collections for the owner of this download job
        collections = [collection.name for collection in Collection.objects.filter_by_access_level(self.owner)]

        # get database adapter
        adapter = DatabaseAdapter()

        # get the schema_name and the table_name from the settings
        schema_name = settings.ARCHIVE_SCHEMA
        table_name = settings.ARCHIVE_TABLE

        # prepare list of files for this archive job
        files = []

        if 'file_ids' in self.data:
            if isinstance(self.data, QueryDict):
                file_ids = self.data.getlist('file_ids')
            else:
                file_ids = self.data.get('file_ids')

            for file_id in file_ids:
                # validate that the file_id is a valid UUID4
                try:
                    uuid.UUID(file_id, version=4)
                except ValueError:
                    raise ValidationError({
                        'files': [_('One or more of the identifiers are not valid UUIDs.')]
                    })

                # fetch the path for this file from the database
                row = adapter.fetch_row(schema_name, table_name, ['path'], filters={
                    'id': file_id,
                    'collection': collections
                })

                # append the file to the list of files only if it exists in the database and on the filesystem
                if row and os.path.isfile(os.path.join(settings.ARCHIVE_BASE_PATH, row[0])):
                    files.append(row[0])
                else:
                    raise ValidationError({
                        'files': [_('One or more of the files cannot be found.')]
                    })

        elif 'search' in self.data:
            # retrieve the pathes of all file matching the search criteria
            rows = adapter.fetch_rows(schema_name, table_name, page_size=0, search=self.data['search'], filters={
                'collection': collections
            })

            # get the index of the path column in the row
            path_index = six.next((i for i, column in enumerate(settings.ARCHIVE_COLUMNS) if column['name'] == 'path'))

            for row in rows:
                # append the file to the list of files only if it exists on the filesystem
                if os.path.isfile(os.path.join(settings.ARCHIVE_BASE_PATH, row[path_index])):
                    files.append(row[path_index])
                else:
                    raise ValidationError({
                        'files': [_('One or more of the files cannot be found.')]
                    })

        else:
            raise ValidationError({
                [_('No data received.')]
            })

        # set files and file_path for this archive job
        self.files = files

        # set clean flag
        self.is_clean = True

    def run(self):
        if not self.is_clean:
            raise Exception('archive_job.process() was not called.')

        if self.phase == self.PHASE_PENDING:
            self.phase = self.PHASE_QUEUED
            self.save()

            archive_job_id = str(self.id)
            if not settings.ASYNC:
                logger.info('archive_job %s submitted (sync)' % archive_job_id)
                create_archive_zip_file.apply((archive_job_id, ), task_id=archive_job_id, throw=True)

            else:
                logger.info('archive_job %s submitted (async, queue=download)' % archive_job_id)
                create_archive_zip_file.apply_async((archive_job_id, ), task_id=archive_job_id, queue='download')

        else:
            raise ValidationError({
                'phase': ['Job is not PENDING.']
            })

    def abort(self):
        pass

    def archive(self):
        pass

    def delete_file(self):
        try:
            os.remove(self.file_path)
        except OSError:
            pass
