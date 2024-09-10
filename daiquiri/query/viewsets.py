import os

from collections import OrderedDict

from django_sendfile import sendfile

from django.conf import settings
from django.http import Http404, FileResponse
from django.utils.timezone import now

from rest_framework import viewsets, mixins, filters, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.decorators import action
from rest_framework.authentication import (
    SessionAuthentication,
    BasicAuthentication,
    TokenAuthentication
)

from daiquiri.core.viewsets import ChoicesViewSet, RowViewSetMixin
from daiquiri.core.permissions import HasModelPermission
from daiquiri.core.paginations import ListPagination
from daiquiri.core.utils import (
    get_client_ip,
    get_file_size,
    fix_for_json,
    filter_by_access_level,
    handle_file_upload,
    import_class
)
from daiquiri.jobs.viewsets import SyncJobViewSet, AsyncJobViewSet
from daiquiri.stats.models import Record

from .models import QueryJob, DownloadJob, Example
from .serializers import (
    FormDetailSerializer,
    FormListSerializer,
    DropdownSerializer,
    DownloadSerializer,
    QueryDownloadFormatSerializer,
    QueryJobSerializer,
    QueryJobListSerializer,
    QueryJobRetrieveSerializer,
    QueryJobCreateSerializer,
    QueryJobFormSerializer,
    QueryJobUpdateSerializer,
    QueryJobUploadSerializer,
    QueryLanguageSerializer,
    ExampleSerializer,
    UserExampleSerializer,
    SyncQueryJobSerializer,
    AsyncQueryJobSerializer
)
from .permissions import HasPermission
from .utils import (
    fetch_user_schema_metadata,
    get_download_config,
    get_format_config,
    get_quota,
    get_user_upload_directory,
    handle_upload_param,
    ingest_uploads
)

from .filters import JobFilterBackend


class StatusViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = (HasPermission, )
    queryset = []

    def list(self, request):
        return Response([{
            'guest': not request.user.is_authenticated,
            'queued_jobs': None,
            'size': QueryJob.objects.get_size(request.user),
            'quota': get_quota(request.user),
            'upload_limit': get_quota(request.user, quota_settings='QUERY_UPLOAD_LIMIT')
        }])


class FormViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    permission_classes = (HasPermission, )

    def get_queryset(self):
        return settings.QUERY_FORMS

    def get_object(self):
        return next(form for form in self.get_queryset() if form.get('key') == self.kwargs.get('pk'))

    def get_serializer_class(self):
        if self.action == 'list':
            return FormListSerializer
        else:
            return FormDetailSerializer



class DropdownViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = (HasPermission, )

    serializer_class = DropdownSerializer

    def get_queryset(self):
        return settings.QUERY_DROPDOWNS


class DownloadViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = (HasPermission, )

    serializer_class = DownloadSerializer

    def get_queryset(self):
        return settings.QUERY_DOWNLOADS


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

        # hide TAP queries for the anonymous user
        if self.request.user.is_anonymous:
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
            owner=(None if self.request.user.is_anonymous else self.request.user),
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

    @action(detail=False, methods=['get'])
    def tables(self, request):
        queryset = self.get_queryset().filter(phase=QueryJob.PHASE_COMPLETED)[:100]
        return Response(fetch_user_schema_metadata(request.user, queryset))

    @action(detail=False, methods=['post'], url_path='forms/(?P<form_key>[a-z]+)', url_name='forms')
    def forms(self, request, form_key):
        # follows CreateModelMixin.create(request, *args, **kwargs)
        serializer = QueryJobFormSerializer(
            data=request.data,
            form_key=form_key,
            context=self.get_serializer_context()
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=['post'], url_path='upload', url_name='upload')
    def upload(self, request):

        if not settings.QUERY_UPLOAD:
            raise Http404

        serializer = QueryJobUploadSerializer(data=request.data, context={
            'request': request,
            'view': self
        })
        serializer.is_valid(raise_exception=True)

        file_name = handle_file_upload(get_user_upload_directory(self.request.user), serializer.validated_data['file'])

        job = QueryJob(
            job_type=QueryJob.JOB_TYPE_INTERFACE,
            owner=(None if self.request.user.is_anonymous else self.request.user),
            run_id=serializer.validated_data.get('run_id'),
            table_name=serializer.validated_data.get('table_name'),
            client_ip=get_client_ip(self.request)
        )
        job.process(upload=True)
        job.save()
        job.ingest(file_name)

        serializer = QueryJobRetrieveSerializer(instance=job)
        return Response(serializer.data)

    @action(detail=True, methods=['put'])
    def abort(self, request, pk=None):
        try:
            job = self.get_queryset().get(pk=pk)
            job.abort()

            serializer = QueryJobRetrieveSerializer(instance=job)
            return Response(serializer.data)
        except QueryJob.DoesNotExist:
            raise Http404

    @action(detail=True, methods=['get'])
    def rows(self, request, pk=None):
        try:
            job = self.get_queryset().get(pk=pk)
        except QueryJob.DoesNotExist:
            raise NotFound

        # get the row query params from the request
        ordering, page, page_size, search, filters = self._get_query_params(job.columns())

        # get column names from the request
        column_names = self.request.GET.getlist('column')

        # get the count and the rows from the job
        count, results = job.rows(column_names, ordering, page, page_size, search, filters)

        # return ordered dict to be send as json
        return Response(OrderedDict((
            ('count', count),
            ('results', fix_for_json(results)),
            ('next', self._get_next_url(page, page_size, count)),
            ('previous', self._get_previous_url(page))
        )))

    @action(detail=True, methods=['get'])
    def columns(self, request, pk=None, format_key=None):
        try:
            job = self.get_queryset().get(pk=pk)
        except QueryJob.DoesNotExist:
            raise NotFound

        return Response(job.columns())

    @action(detail=True, methods=['get'], url_name='download',
            url_path=r'download/(?P<download_key>[a-z\-]+)/(?P<download_job_id>[A-Za-z0-9\-]+)')
    def download(self, request, pk=None, download_key=None, download_job_id=None):
        try:
            self.get_queryset().get(pk=pk)
        except QueryJob.DoesNotExist:
            raise NotFound

        download_config = get_download_config(download_key)
        if download_config is None:
            raise ValidationError({'download': 'Download key "{}" is not supported.'.format(download_key)})

        download_job_model = import_class(download_config['model'])

        try:
            download_job = download_job_model.objects.get(query_job=pk, pk=download_job_id)
        except download_job_model.DoesNotExist:
            raise NotFound

        if download_job.phase == download_job.PHASE_COMPLETED and request.GET.get('download', True):
            Record.objects.create(
                time=now(),
                resource_type='DOWNLOAD',
                resource={
                    'job_id': download_job.id,
                    'job_type': download_job.job_type,
                    'file_path': download_job.file_path
                },
                client_ip=download_job.client_ip,
                user=download_job.owner,
                size=os.path.getsize(download_job.file_path)
            )
            return sendfile(request, download_job.file_path, attachment=True)
        else:
            return Response({
                'phase': download_job.phase,
                'size': get_file_size(download_job.file_path),
            })

    @action(detail=True, methods=['post'], url_name='create-download',
            url_path=r'download/(?P<download_key>[a-z\-]+)')
    def create_download(self, request, pk=None, download_key=None):
        try:
            job = self.get_queryset().get(pk=pk)
        except QueryJob.DoesNotExist:
            raise NotFound

        download_config = get_download_config(download_key)
        if download_config is None:
            raise ValidationError({'download': 'Download key "{}" is not supported.'.format(download_key)})

        download_job_model = import_class(download_config['model'])

        params = {param: request.data.get(param) for param in download_config.get('params', [])}

        try:
            download_job = download_job_model.objects.get(query_job=job, **params)

            # check if the file was lost
            if download_job.phase == download_job.PHASE_COMPLETED and \
                    not os.path.isfile(download_job.file_path):

                # set the phase back to pending so that the file is recreated
                download_job.phase = download_job.PHASE_PENDING
                download_job.process()
                download_job.save()
                download_job.run()

        except download_job_model.DoesNotExist:
            download_job = download_job_model(
                job_type=QueryJob.JOB_TYPE_INTERFACE,
                owner=(None if self.request.user.is_anonymous else self.request.user),
                client_ip=get_client_ip(self.request),
                query_job=job,
                **params
            )
            download_job.process()
            download_job.save()
            download_job.run()

        return Response({
            'id': download_job.id
        })

    @action(detail=True, methods=['get'], url_path=r'stream/(?P<format_key>[A-Za-z0-9\-]+)', url_name='stream')
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
            download_job = DownloadJob.objects.get(query_job=job, format_key=format_key)

            # check if the file was lost
            if download_job.phase == download_job.PHASE_COMPLETED and os.path.isfile(download_job.file_path):
                # stream the previously created file
                return sendfile(request, download_job.file_path)
        except DownloadJob.DoesNotExist:
            pass

        # stream the table directly from the database
        response = FileResponse(job.stream(format_key), content_type=format_config['content_type'])
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

    @action(detail=False, methods=['get'], permission_classes=(HasPermission, ))
    def user(self, request):
        examples = Example.objects.filter_by_access_level(self.request.user)
        serializer = UserExampleSerializer(examples, many=True)
        return Response(serializer.data)


class QueueViewSet(ChoicesViewSet):
    permission_classes = (HasPermission, )

    def get_queryset(self):
        items = filter_by_access_level(self.request.user, settings.QUERY_QUEUES)
        return [(item['key'], item['label']) for item in items]


class QueryLanguageViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = (HasPermission, )
    serializer_class = QueryLanguageSerializer

    def get_queryset(self):
        return filter_by_access_level(self.request.user, settings.QUERY_LANGUAGES)


class QueryDownloadFormatViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = (HasPermission, )
    serializer_class = QueryDownloadFormatSerializer

    def get_queryset(self):
        return settings.QUERY_DOWNLOAD_FORMATS


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

    def handle_upload(self, job, upload_string):
        job.uploads = handle_upload_param(self.request, upload_string)
        ingest_uploads(job.uploads, job.owner)


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

    def handle_upload(self, job, upload_string):
        job.uploads = handle_upload_param(self.request, upload_string)
