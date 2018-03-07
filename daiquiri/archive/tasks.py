from __future__ import absolute_import, unicode_literals

import logging
import os
import zipfile

from django.conf import settings
from django.utils.timezone import now

from celery import shared_task

from daiquiri.core.tasks import Task


@shared_task(track_started=True, base=Task)
def create_archive_zip_file(archive_job_id):
    # always import daiquiri packages inside the task
    from daiquiri.archive.models import ArchiveJob

    # get logger
    logger = logging.getLogger(__name__)

    # get the job object from the database
    archive_job = ArchiveJob.objects.get(pk=archive_job_id)

    # log start
    logger.info('archive_job %s started' % archive_job.file_path)

    # create directory if necessary
    try:
        os.makedirs(os.path.dirname(archive_job.file_path))
    except OSError:
        pass

    archive_job.phase = archive_job.PHASE_EXECUTING
    archive_job.start_time = now()
    archive_job.save()

    # create a zipfile with all files
    with zipfile.ZipFile(archive_job.file_path, 'w') as z:
        for file_path in archive_job.files:
            os.chdir(settings.ARCHIVE_BASE_PATH)
            z.write(file_path)

    archive_job.end_time = now()
    archive_job.phase = archive_job.PHASE_COMPLETED
    archive_job.save()

    # log completion
    logger.info('archive_job %s completed' % archive_job.file_path)
