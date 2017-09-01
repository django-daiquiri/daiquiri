import logging
import os

from celery.result import AsyncResult, EagerResult

from sendfile import sendfile

from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse, Http404

from daiquiri.metadata.models import Database, Table
from daiquiri.query.models import QueryJob

from .tasks import create_download_archive
from .utils import get_columns, get_file, get_files, get_download_file_name

logger = logging.getLogger(__name__)


def table(request, database_name, table_name):

    try:
        get_columns(request.user, database_name, table_name)
    except (QueryJob.DoesNotExist, Database.DoesNotExist, Table.DoesNotExist):
        raise Http404

    return render(request, 'serve/table.html', {
        'database': database_name,
        'table': table_name
    })


def files(request, file_path):

    file = get_file(request.user, file_path)

    if file:
        return sendfile(request, file, attachment=False)

    raise Http404


def archive(request, database_name, table_name, column_name):

    files = get_files(request.user, database_name, table_name, column_name)
    if files:
        file_name = get_download_file_name(request.user, table_name, column_name)

        task_id = file_name
        task_args = (file_name, files)

        if not settings.ASYNC:
            if os.path.isfile(file_name):
                task_result = EagerResult(task_id, None, 'SUCCESS')
            else:
                logger.info('create_download_archive %s submitted (sync)' % file_name)
                task_result = create_download_archive.apply(task_args, task_id=task_id, throw=True)

        else:
            task_result = AsyncResult(task_id)

            if not os.path.isfile(file_name):
                # create an empty file to prevent multiple pending tasks
                open(file_name, 'a').close()

                if task_result.successful():
                    # somebody or something removed the file. start all over again
                    task_result.forget()

                logger.info('create_download_archive %s submitted (async, queue=download)' % file_name)
                task_result = create_download_archive.apply_async(task_args, task_id=task_id)

        if task_result.successful():
            if request.method == 'GET':
                return sendfile(request, file_name, attachment=True)
            else:
                return HttpResponse(task_result.status)

        else:
            if task_result.status == 'FAILURE':
                return HttpResponse(task_result.status, status=500)
            else:
                return HttpResponse(task_result.status)

    # if nothing worked, return 404
    raise Http404
