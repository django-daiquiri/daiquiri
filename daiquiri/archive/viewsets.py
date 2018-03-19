import os

from collections import OrderedDict

from sendfile import sendfile

from django.conf import settings
from django.utils.timezone import now

from rest_framework import viewsets, serializers
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

from daiquiri.core.viewsets import RowViewSetMixin
from daiquiri.core.adapter import DatabaseAdapter
from daiquiri.core.utils import get_client_ip
from daiquiri.stats.models import Record

from .models import Collection, ArchiveJob

from .permissions import HasPermission


class RowViewSet(RowViewSetMixin, viewsets.GenericViewSet):
    permission_classes = (HasPermission, )

    def list(self, request, *args, **kwargs):
        # fetch rows from the database
        column_names = [column['name'] for column in settings.ARCHIVE_COLUMNS]

        # get the row query params from the request
        ordering, page, page_size, search, filters = self._get_query_params(column_names)

        # get database adapter
        adapter = DatabaseAdapter()

        # get the schema_name and the table_name from the settings
        schema_name = settings.ARCHIVE_SCHEMA
        table_name = settings.ARCHIVE_TABLE

        # get collecions for this user and add them to the filters
        collections = [collection.name for collection in Collection.objects.filter_by_access_level(request.user)]
        filters['collection'] = collections

        # query the database for the total number of rows
        count = adapter.count_rows(schema_name, table_name, column_names, search, filters)

        # query the paginated rowset
        results = adapter.fetch_rows(schema_name, table_name, column_names, ordering, page, page_size, search, filters)

        # return ordered dict to be send as json
        return Response(OrderedDict((
            ('count', count),
            ('results', results),
            ('next', self._get_next_url(page, page_size, count)),
            ('previous', self._get_previous_url(page))
        )))


class ColumnViewSet(viewsets.ViewSet):
    permission_classes = (HasPermission, )

    def list(self, request, *args, **kwargs):

        return Response(settings.ARCHIVE_COLUMNS)


class FileViewSet(viewsets.GenericViewSet):
    permission_classes = (HasPermission, )
    serializer_class = serializers.Serializer

    def retrieve(self, request, pk=None):
        # get database adapter
        adapter = DatabaseAdapter()

        # get the schema_name and the table_name from the settings
        schema_name = settings.ARCHIVE_SCHEMA
        table_name = settings.ARCHIVE_TABLE

        # get collecions for this user
        collections = [collection.name for collection in Collection.objects.filter_by_access_level(request.user)]

        # fetch the path for this file from the database
        row = adapter.fetch_row(schema_name, table_name, ['path'], filters={
            'id': pk,
            'collection': collections
        })

        if row:
            if request.GET.get('download', True):
                # create a stats record for this download
                Record.objects.create(
                    time=now(),
                    resource_type='ARCHIVE_DOWNLOAD',
                    resource=row[0],
                    client_ip=get_client_ip(request),
                    user=request.user if request.user.is_authenticated else None
                )

                # send the file to the client
                file_path = os.path.join(settings.ARCHIVE_BASE_PATH, row[0])
                return sendfile(request, file_path, attachment=True)
            else:
                # send an empty response
                return Response()

        # if the file was not found, return 404
        raise NotFound()


class ArchiveViewSet(viewsets.GenericViewSet):
    permission_classes = (HasPermission, )
    serializer_class = serializers.Serializer

    def retrieve(self, request, pk=None):
        try:
            archive_job = ArchiveJob.objects.filter_by_owner(request.user).get(pk=pk)
        except ArchiveJob.DoesNotExist:
            raise NotFound

        if archive_job.phase == archive_job.PHASE_COMPLETED and request.GET.get('download', True):
            return sendfile(request, archive_job.file_path, attachment=True)
        else:
            return Response(archive_job.phase)

    def create(self, request):
        try:
            archive_job = ArchiveJob.objects.filter_by_owner(request.user).get(data=request.data)

            # check if the file was lost
            if archive_job.phase == archive_job.PHASE_COMPLETED and \
                    not os.path.isfile(archive_job.file_path):

                # set the phase back to pending so that the file is recreated
                archive_job.phase = archive_job.PHASE_PENDING
                archive_job.process()
                archive_job.save()
                archive_job.run()

        except ArchiveJob.DoesNotExist:
            archive_job = ArchiveJob(
                owner=(None if self.request.user.is_anonymous() else self.request.user),
                client_ip=get_client_ip(self.request),
                data=request.data
            )
            archive_job.process()
            archive_job.save()
            archive_job.run()

        return Response({
            'id': archive_job.id
        })
