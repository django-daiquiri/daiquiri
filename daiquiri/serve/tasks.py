from __future__ import absolute_import, unicode_literals

import logging
import os
import zipfile

from celery import shared_task

from daiquiri.core.tasks import Task


@shared_task(track_started=True, base=Task)
def create_download_archive(file_name, files):
    # get logger
    logger = logging.getLogger(__name__)

    # log start
    logger.info('create_download_archive %s started' % file_name)

    # create directory if necessary
    try:
        os.mkdir(os.path.dirname(file_name))
    except OSError:
        pass

    # create a zipfile with all files
    with zipfile.ZipFile(file_name, 'w') as z:
        for directory_path, file_path in files:
            os.chdir(directory_path)
            z.write(file_path)

    # log completion
    logger.info('create_download_archive %s completed' % file_name)
