import logging
import os
import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from rest_framework.exceptions import ValidationError

from jsonfield import JSONField

from daiquiri.jobs.models import Job

from .utils import get_archive_file_path
from .tasks import create_archive_zip_file

logger = logging.getLogger(__name__)


class ArchiveJob(Job):

    data = JSONField(
        verbose_name=_('Data'),
        help_text=_('Input data for archive creation.')
    )
    files = JSONField(
        verbose_name=_('Files'),
        help_text=_('List of files in the archive.')
    )
    file_path = models.CharField(
        max_length=256,
        verbose_name=_('Path'),
        help_text=_('Path to the archive file.')
    )

    class Meta:
        ordering = ('start_time', )

        verbose_name = _('ArchiveJob')
        verbose_name_plural = _('ArchiveJobs')

        permissions = (('view_archivejob', 'Can view ArchiveJob'),)

    @property
    def parameters(self):
        return None

    @property
    def results(self):
        return None

    @property
    def result(self):
        return None

    @property
    def quote(self):
        return None

    def process(self):
        from daiquiri.core.adapter import get_adapter

        database_name = settings.ARCHIVE_DATABASE
        table_name = settings.ARCHIVE_TABLE

        adapter = get_adapter()

        # prepare list of files for this archive job
        files = []

        if 'file_ids' in self.data:

            for file_id in self.data['file_ids']:
                # validate that the file_id is a valid UUID4
                try:
                    uuid.UUID(file_id, version=4)
                except ValueError:
                    raise ValidationError({
                        'files': [_('One or more of the identifiers are not valid UUIDs.')]
                    })

                # get the path to the file from the database
                file = adapter.database.fetch_dict(database_name, table_name, ['path'], filters={
                    'id': file_id
                })

                # append the file to the list of files only if it exists in the database and on the filesystem
                if file and os.path.isfile(os.path.join(settings.ARCHIVE_BASE_PATH, file['path'])):
                    files.append(file['path'])
                else:
                    raise ValidationError({
                        'files': [_('One or more of the file cannot be found.')]
                    })

        elif 'search' in self.data:

            # retrieve the pathes of all file matching the search criteria
            rows = adapter.database.fetch_rows(database_name, table_name, ['path'], search=self.data['search'], page_size=0)

            for row in rows:
                # append the file to the list of files only if it exists on the filesystem
                if os.path.isfile(os.path.join(settings.ARCHIVE_BASE_PATH, row[0])):
                    files.append(row[0])
                else:
                    raise ValidationError({
                        'files': [_('One or more of the file cannot be found.')]
                    })

        else:
            raise ValidationError({
                [_('No data received.')]
            })

        # set files and file_path for this archive job
        self.files = files
        self.file_path = get_archive_file_path(self.owner, self.id)

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
                logger.info('create_archive_zip_file %s submitted (sync)' % archive_job_id)
                create_archive_zip_file.apply((archive_job_id, ), task_id=archive_job_id, throw=True)

            else:
                logger.info('create_archive_zip_file %s submitted (async, queue=download)' % archive_job_id)
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
        os.remove(self.file_path)
