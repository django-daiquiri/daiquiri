import os

from collections import OrderedDict

from sendfile import sendfile

from django.conf import settings
from django.utils.timezone import now

from rest_framework import viewsets, serializers
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

from daiquiri.core.viewsets import RowViewSet as BaseRowViewSet
from daiquiri.core.utils import get_client_ip
from daiquiri.stats.models import Record

from .models import Collection, ArchiveJob
from .utils import count_rows, fetch_rows, fetch_row


class RowViewSet(BaseRowViewSet):

    def list(self, request, *args, **kwargs):
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

        # get collecions for this user
        collections = [collection.name for collection in Collection.objects.filter_by_access_level(request.user)]

        # fetch rows from the database
        column_names = [column['name'] for column in settings.ARCHIVE_COLUMNS]
        count = count_rows(collections, column_names, search, filters)
        results = fetch_rows(collections, column_names, ordering, page, page_size, search, filters)

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
        # get collecions for this user
        collections = [collection.name for collection in Collection.objects.filter_by_access_level(request.user)]

        row = fetch_row(collections, ['path'], pk)
        if row:
            if request.GET.get('download', True):
                # create a stats record for this download
                Record.objects.create(
                    time=now(),
                    resource_type='ARCHIVE_DOWNLOAD',
                    resource=row[0],
                    client_ip=get_client_ip(request),
                    user=request.user
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

    serializer_class = serializers.Serializer

    def retrieve(self, request, pk=None):
        try:
            archive_job = ArchiveJob.objects.get(pk=pk)
        except ArchiveJob.DoesNotExist:
            raise NotFound

        if archive_job.phase == archive_job.PHASE_COMPLETED and request.GET.get('download', True):
            return sendfile(request, archive_job.file_path, attachment=True)
        else:
            return Response(archive_job.phase)

    def create(self, request):
        try:
            archive_job = ArchiveJob.objects.get(owner=request.user, data=request.data)

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
                owner=request.user,
                client_ip=get_client_ip(self.request),
                data=request.data
            )
            archive_job.process()
            archive_job.save()
            archive_job.run()

        return Response({
            'id': archive_job.id
        })
