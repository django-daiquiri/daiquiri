import os

from collections import OrderedDict

from sendfile import sendfile

from django.conf import settings
from django.http import Http404, FileResponse

from rest_framework import viewsets, mixins, filters
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.decorators import list_route, detail_route
from rest_framework.authentication import (
    SessionAuthentication,
    BasicAuthentication,
    TokenAuthentication
)

from daiquiri.core.viewsets import ChoicesViewSet, RowViewSetMixin
from daiquiri.core.permissions import HasModelPermission
from daiquiri.core.paginations import ListPagination
from daiquiri.core.utils import get_client_ip, replace_nan
from daiquiri.jobs.viewsets import SyncJobViewSet, AsyncJobViewSet

from .models import QueryJob, DownloadJob, QueryArchiveJob, Example
from .serializers import (
    FormSerializer,
    DropdownSerializer,
    QueryJobSerializer,
    QueryJobListSerializer,
    QueryJobRetrieveSerializer,
    QueryJobCreateSerializer,
    QueryJobUpdateSerializer,
    QueryLanguageSerializer,
    ExampleSerializer,
    UserExampleSerializer,
    SyncQueryJobSerializer,
    AsyncQueryJobSerializer
)
from .permissions import HasPermission
from .utils import get_format_config, get_quota, fetch_user_schema_metadata
from .filters import JobFilterBackend


class StatusViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = (HasPermission, )
    queryset = []

    def list(self, request):
        return Response([{
            'guest': not request.user.is_authenticated(),
            'queued_jobs': None,
            'size': QueryJob.objects.get_size(request.user),
            'quota': get_quota(request.user)
        }])


class FormViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = (HasPermission, )

    serializer_class = FormSerializer

    def get_queryset(self):
        return settings.QUERY_FORMS


class DropdownViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = (HasPermission, )

    serializer_class = DropdownSerializer

    def get_queryset(self):
        return settings.QUERY_DROPDOWNS


class QueryJobViewSet(RowViewSetMixin, viewsets.ModelViewSet):
    permission_classes = (HasPermission, )
    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)
    pagination_class = ListPagination

    filter_backends = (
        filters.SearchFilter,
        filters.OrderingFilter,
        JobFilterBackend
    )
    search_fields = ('id', 'run_id', 'table_name', 'phase')
    filter_fields = ('phase', )

    def get_queryset(self):
        queryset = QueryJob.objects.filter_by_owner(self.request.user).order_by('-creation_time')

        # hide TAP jobs in the list for the anonymous user
        if self.action == 'list' and self.request.user.is_anonymous:
            queryset = queryset.filter(job_type=QueryJob.JOB_TYPE_INTERFACE)

        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return QueryJobListSerializer
        elif self.action == 'retrieve' or self.action == 'abort':
            return QueryJobRetrieveSerializer
        elif self.action == 'create':
            return QueryJobCreateSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return QueryJobUpdateSerializer
        else:
            return QueryJobSerializer

    def get_throttles(self):
        if self.action == 'create':
            self.throttle_scope = 'query.create'

        return super(QueryJobViewSet, self).get_throttles()

    def perform_create(self, serializer):
        job = QueryJob(
            job_type=QueryJob.JOB_TYPE_INTERFACE,
            owner=(None if self.request.user.is_anonymous() else self.request.user),
            run_id=serializer.data.get('run_id'),
            table_name=serializer.data.get('table_name'),
            query_language=serializer.data.get('query_language'),
            query=serializer.data.get('query'),
            queue=serializer.data.get('queue'),
            client_ip=get_client_ip(self.request)
        )
        job.process()
        job.save()
        job.run()

        # inject the job id into the serializers data
        serializer._data['id'] = job.id

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        instance.archive()

    @list_route(methods=['get'])
    def tables(self, request):
        return Response(fetch_user_schema_metadata(request.user, self.get_queryset()))

    @detail_route(methods=['put'])
    def abort(self, request, pk=None):
        try:
            job = self.get_queryset().get(pk=pk)
            job.abort()

            serializer = QueryJobRetrieveSerializer(instance=job)
            return Response(serializer.data)
        except QueryJob.DoesNotExist:
            raise Http404

    @detail_route(methods=['get'])
    def rows(self, request, pk=None):
        try:
            job = self.get_queryset().get(pk=pk)
        except QueryJob.DoesNotExist:
            raise NotFound

        # get column names from the request
        column_names = self.request.GET.getlist('column')

        # get the row query params from the request
        ordering, page, page_size, search, filters = self._get_query_params(column_names)

        # get the count and the rows from the job
        count, results = job.rows(column_names, ordering, page, page_size, search, filters)

        replace_nan(results)

        # return ordered dict to be send as json
        return Response(OrderedDict((
            ('count', count),
            ('results', results),
            ('next', self._get_next_url(page, page_size, count)),
            ('previous', self._get_previous_url(page))
        )))

    @detail_route(methods=['get'])
    def columns(self, request, pk=None, format_key=None):
        try:
            job = self.get_queryset().get(pk=pk)
        except QueryJob.DoesNotExist:
            raise NotFound

        return Response(job.columns())

    @detail_route(methods=['get'], url_path='download/(?P<download_id>[A-Za-z0-9\-]+)', url_name='download')
    def download(self, request, pk=None, download_id=None):
        try:
            job = self.get_queryset().get(pk=pk)
        except QueryJob.DoesNotExist:
            raise NotFound

        try:
            download_job = job.downloads.get(pk=download_id)
        except DownloadJob.DoesNotExist:
            raise NotFound

        if download_job.phase == download_job.PHASE_COMPLETED and request.GET.get('download', True):
            return sendfile(request, download_job.file_path, attachment=True)
        else:
            return Response(download_job.phase)

    @detail_route(methods=['post'], url_path='download', url_name='create-download')
    def create_download(self, request, pk=None):
        try:
            job = self.get_queryset().get(pk=pk)
        except QueryJob.DoesNotExist:
            raise NotFound

        format_key = request.data.get('format_key')

        try:
            download_job = DownloadJob.objects.get(job=job, format_key=format_key)

            # check if the file was lost
            if download_job.phase == download_job.PHASE_COMPLETED and \
                    not os.path.isfile(download_job.file_path):

                # set the phase back to pending so that the file is recreated
                download_job.phase = download_job.PHASE_PENDING
                download_job.process()
                download_job.save()
                download_job.run()

        except DownloadJob.DoesNotExist:
            download_job = DownloadJob(
                client_ip=get_client_ip(self.request),
                job=job,
                format_key=format_key
            )
            download_job.process()
            download_job.save()
            download_job.run()

        return Response({
            'id': download_job.id
        })

    @detail_route(methods=['get'], url_path='archive/(?P<archive_id>[A-Za-z0-9\-]+)', url_name='archive')
    def archive(self, request, pk=None, archive_id=None):
        try:
            job = self.get_queryset().get(pk=pk)
        except QueryJob.DoesNotExist:
            raise NotFound

        try:
            archive_job = job.archives.get(pk=archive_id)
        except QueryArchiveJob.DoesNotExist:
            raise NotFound

        if archive_job.phase == archive_job.PHASE_COMPLETED and request.GET.get('download', True):
            return sendfile(request, archive_job.file_path, attachment=True)
        else:
            return Response(archive_job.phase)

    @detail_route(methods=['post'], url_path='archive', url_name='create-archive')
    def create_archive(self, request, pk=None):
        try:
            job = self.get_queryset().get(pk=pk)
        except QueryJob.DoesNotExist:
            raise NotFound

        column_name = request.data.get('column_name')

        try:
            archive_job = QueryArchiveJob.objects.get(job=job, column_name=column_name)

            # check if the file was lost
            if archive_job.phase == archive_job.PHASE_COMPLETED and \
                    not os.path.isfile(archive_job.file_path):

                # set the phase back to pending so that the file is recreated
                archive_job.phase = archive_job.PHASE_PENDING
                archive_job.process()
                archive_job.save()
                archive_job.run()

        except QueryArchiveJob.DoesNotExist:
            archive_job = QueryArchiveJob(
                client_ip=get_client_ip(self.request),
                job=job,
                column_name=column_name
            )
            archive_job.process()
            archive_job.save()
            archive_job.run()

        return Response({
            'id': archive_job.id
        })

    @detail_route(methods=['get'], url_path='stream/(?P<format_key>[A-Za-z0-9\-]+)', url_name='stream')
    def stream(self, request, pk=None, format_key=None):
        try:
            job = self.get_queryset().get(pk=pk)
        except QueryJob.DoesNotExist:
            raise NotFound

        try:
            format_config = get_format_config(format_key)
        except IndexError:
            raise ValidationError({'format': "Not supported."})

        try:
            download_job = DownloadJob.objects.get(job=job, format_key=format_key)

            # check if the file was lost
            if download_job.phase == download_job.PHASE_COMPLETED and os.path.isfile(download_job.file_path):
                # stream the previously created file
                return sendfile(request, download_job.file_path, attachment=True)
        except DownloadJob.DoesNotExist:
            pass

        # stream the table directly from the database
        file_name = '%s.%s' % (job.table_name, format_config['extension'])
        response = FileResponse(job.stream(format_key), content_type=format_config['content_type'])
        response['Content-Disposition'] = "attachment; filename=%s" % file_name
        return response


class ExampleViewSet(viewsets.ModelViewSet):
    permission_classes = (HasModelPermission, )
    serializer_class = ExampleSerializer
    pagination_class = ListPagination
    queryset = Example.objects.all()

    filter_backends = (
        filters.SearchFilter,
        filters.OrderingFilter
    )
    search_fields = ('name', 'description', 'query_string')

    @list_route(methods=['get'], permission_classes=(HasPermission, ))
    def user(self, request):
        examples = Example.objects.filter_by_access_level(self.request.user)
        serializer = UserExampleSerializer(examples, many=True)
        return Response(serializer.data)


class QueueViewSet(ChoicesViewSet):
    permission_classes = (HasPermission, )
    queryset = [(item['key'], item['label']) for item in settings.QUERY_QUEUES]


class QueryLanguageViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = (HasPermission, )
    serializer_class = QueryLanguageSerializer
    queryset = settings.QUERY_LANGUAGES


class PhaseViewSet(ChoicesViewSet):
    permission_classes = (HasPermission, )
    authentication_classes = (SessionAuthentication, TokenAuthentication)
    queryset = QueryJob.PHASE_CHOICES


class SyncQueryJobViewSet(SyncJobViewSet):
    permission_classes = (HasPermission, )
    serializer_class = SyncQueryJobSerializer

    parameter_map = {
        'FORMAT': 'response_format',
        'TABLE_NAME': 'table_name',
        'LANG': 'query_language',
        'QUERY': 'query'
    }

    def get_queryset(self):
        return QueryJob.objects.filter_by_owner(self.request.user)


class AsyncQueryJobViewSet(AsyncJobViewSet):
    permission_classes = (HasPermission, )
    serializer_class = AsyncQueryJobSerializer

    parameter_map = {
        'FORMAT': 'response_format',
        'TABLE_NAME': 'table_name',
        'LANG': 'query_language',
        'QUEUE': 'queue',
        'QUERY': 'query'
    }

    def get_queryset(self):
        return QueryJob.objects.filter_by_owner(self.request.user)
