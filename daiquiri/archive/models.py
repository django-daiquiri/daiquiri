import logging
import os
import uuid

from django.conf import settings
from django.contrib.auth.models import Group
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from rest_framework.exceptions import ValidationError

from jsonfield import JSONField

from daiquiri.core.constants import ACCESS_LEVEL_CHOICES
from daiquiri.core.managers import AccessLevelManager
from daiquiri.jobs.models import Job

from .utils import fetch_rows, fetch_row, get_archive_file_path
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
        # get collections for the owner of this download job
        collections = [collection.name for collection in Collection.objects.filter_by_access_level(self.owner)]

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
                row = fetch_row(collections, ['path'], file_id)

                # append the file to the list of files only if it exists in the database and on the filesystem
                if row and os.path.isfile(os.path.join(settings.ARCHIVE_BASE_PATH, row[0])):
                    files.append(row[0])
                else:
                    raise ValidationError({
                        'files': [_('One or more of the file cannot be found.')]
                    })

        elif 'search' in self.data:

            # retrieve the pathes of all file matching the search criteria
            rows = fetch_rows(collections, ['path'], None, 1, 0, self.data['search'], {})

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
