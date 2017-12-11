import os
import uuid
import logging

from collections import OrderedDict

from sendfile import sendfile

from celery.result import AsyncResult, EagerResult
from celery.task.control import revoke

from django.conf import settings
from django.http import Http404
from django.utils.timezone import now

from rest_framework import viewsets, serializers
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.decorators import list_route

from daiquiri.core.viewsets import RowViewSet as BaseRowViewSet
from daiquiri.core.adapter import get_adapter
from daiquiri.core.utils import get_client_ip
from daiquiri.stats.models import Record

from .utils import get_download_file_name
from .tasks import create_archive_zip

logger = logging.getLogger(__name__)


class RowViewSet(BaseRowViewSet):

    def list(self, request, *args, **kwargs):

        adapter = get_adapter()

        database_name = settings.ARCHIVE_DATABASE
        table_name = settings.ARCHIVE_TABLE
        column_names = [column['name'] for column in settings.ARCHIVE_COLUMNS]

        # get the ordering
        ordering = self.request.GET.get('ordering')

        # get the search string
        search = self.request.GET.get('search')

        # get additional filters from the querystring
        filters = self._get_filters()

        # get the page from the querystring and make sure it is an int
        page = self._get_page()

        # get the page_size from the querystring and make sure it is an int
        page_size = self._get_page_size()

        # query the database for the total number of rows
        count = adapter.database.count_rows(database_name, table_name, column_names, search, filters)

        # # query the paginated rowset
        results = adapter.database.fetch_rows(database_name, table_name, column_names, ordering, page, page_size, search, filters)

        # get the previous and next url
        next = self._get_next_url(page, page_size, count)
        previous = self._get_previous_url(page)

        return Response(OrderedDict((
            ('count', count),
            ('next', next),
            ('previous', previous),
            ('results', results)
        )))


class ColumnViewSet(viewsets.ViewSet):

    def list(self, request, *args, **kwargs):

        return Response(settings.ARCHIVE_COLUMNS)


class FileViewSet(viewsets.GenericViewSet):

    serializer_class = serializers.Serializer

    def retrieve(self, request, pk=None):

        adapter = get_adapter()

        database_name = settings.ARCHIVE_DATABASE
        table_name = settings.ARCHIVE_TABLE
        column_names = [column['name'] for column in settings.ARCHIVE_COLUMNS]

        resource = adapter.database.fetch_dict(database_name, table_name, column_names, filters={
            'id': pk
        })

        if resource:
            if request.GET.get('download', True):
                # create a stats record for this download
                Record.objects.create(
                    time=now(),
                    resource_type='ARCHIVE_DOWNLOAD',
                    resource=resource,
                    client_ip=get_client_ip(request),
                    user=request.user
                )

                # send the file to the client
                file_path = os.path.join(settings.ARCHIVE_BASE_PATH, resource['path'])

                return sendfile(request, file_path, attachment=True)
            else:
                # send an empty response
                return Response()

        # if the file was not found, return 404
        raise NotFound()

    @list_route(methods=['get', 'post'])
    def zip(self, request):

        adapter = get_adapter()

        database_name = settings.ARCHIVE_DATABASE
        table_name = settings.ARCHIVE_TABLE
        column_names = [column['name'] for column in settings.ARCHIVE_COLUMNS]

        task_id = str(uuid.uuid4())
        file_name = get_download_file_name(self.request.user, task_id)

        files = []
        for file_id in request.data:
            resource = adapter.database.fetch_dict(database_name, table_name, column_names, filters={
                'id': file_id
            })

            files.append((settings.ARCHIVE_BASE_PATH, resource['path']))

        task_args = (file_name, files)

        if not settings.ASYNC:
            task_result = create_archive_zip.apply(task_args, task_id=task_id, throw=True)

        else:
            task_result = create_archive_zip.apply_async(task_args, task_id=task_id, queue='download')

        return Response({
            'id': task_id,
            'status': task_result.status
        })
