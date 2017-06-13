import json
from sendfile import sendfile

from django.conf import settings
from django.db.models import Sum
from django.http import Http404
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from rest_framework import viewsets, mixins, filters
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import list_route, detail_route

from daiquiri.core.viewsets import ChoicesViewSet
from daiquiri.core.permissions import HasModelPermission
from daiquiri.core.utils import human2bytes
from daiquiri.core.paginations import ListPagination
from daiquiri.uws.settings import PHASE_ARCHIVED

from .models import QueryJob, Example
from .serializers import (
    FormSerializer,
    DropdownSerializer,
    QueryJobListSerializer,
    QueryJobRetrieveSerializer,
    QueryJobCreateSerializer,
    QueryJobUpdateSerializer,
    ExampleSerializer,
    UserExampleSerializer
)
from .exceptions import (
    ADQLSyntaxError,
    MySQLSyntaxError,
    PermissionError,
    TableError,
    ConnectionError
)
from utils import fetch_user_database_metadata


class StatusViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        return []

    def list(self, request):
        # get quota from settings
        quota = 0
        for group in request.user.groups.all():
            group_quota = settings.QUERY['quota'].get(group.name)
            if group_quota:
                group_quota = human2bytes(group_quota)
                quota = group_quota if group_quota > quota else quota

        # get the size of all the tables of this user
        jobs = QueryJob.objects.filter(owner=self.request.user).exclude(phase=PHASE_ARCHIVED)
        size = jobs.aggregate(Sum('size'))['size__sum']

        return Response([{
            'guest': not request.user.is_authenticated(),
            'queued_jobs': None,
            'size': size,
            'quota': quota
        }])


class FormViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated, )

    serializer_class = FormSerializer

    def get_queryset(self):
        return settings.QUERY['forms']


class DropdownViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated, )

    serializer_class = DropdownSerializer

    def get_queryset(self):
        return settings.QUERY['dropdowns']


class QueryJobViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        return QueryJob.objects.filter(owner=self.request.user).exclude(phase=PHASE_ARCHIVED)

    def get_serializer_class(self):
        if self.action == 'list':
            return QueryJobListSerializer
        elif self.action == 'retrieve' or self.action == 'kill':
            return QueryJobRetrieveSerializer
        elif self.action == 'create':
            return QueryJobCreateSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return QueryJobUpdateSerializer

    def perform_create(self, serializer):

        if 'query' not in serializer.data:
            raise ValidationError({
                'query': {
                    'messages': [_('Value is required and can\'t be empty')]
                }
            })

        if 'table_name' in serializer.data:
            table_name = serializer.data['table_name']
        else:
            table_name = now().strftime("%Y-%m-%d-%H-%M-%S")

        try:
            job_id = QueryJob.objects.submit(
                serializer.data['query_language'],
                serializer.data['query'],
                serializer.data['queue'],
                table_name,
                self.request.user
            )

            # inject the job id into the serializers data
            serializer._data['id'] = job_id

        except (ADQLSyntaxError, MySQLSyntaxError) as e:
            raise ValidationError({
                'query': {
                    'messages': [_('There has been an error while parsing your query.')],
                    'positions': json.dumps(e.message),
                }
            })
        except (PermissionError, ConnectionError) as e:
            raise ValidationError({'query': {'messages': e.message}})
        except TableError as e:
            raise ValidationError({'table_name': e.message})

    def perform_update(self, serializer):
        try:
            serializer.save()
        except TableError as e:
            raise ValidationError({'table_name': [e.message]})

    def perform_destroy(self, instance):
        instance.archive()

    @list_route(methods=['get'])
    def tables(self, request):
        jobs = QueryJob.objects.filter(owner=self.request.user).exclude(phase=PHASE_ARCHIVED)
        return Response([fetch_user_database_metadata(jobs, request.user.username)])

    @detail_route(methods=['put'])
    def kill(self, request, pk=None):
        try:
            job = self.get_queryset().get(pk=pk)
            job.kill()

            serializer = QueryJobRetrieveSerializer(instance=job)
            return Response(serializer.data)
        except QueryJob.DoesNotExist:
            raise Http404

    @detail_route(methods=['put'], url_path='download/(?P<format_key>\w+)')
    def download(self, request, pk=None, format_key=None):
        try:
            format = [f for f in settings.QUERY['download_formats'] if f['key'] == format_key][0]
        except IndexError:
            raise ValidationError({'format': "Not supported."})

        try:
            job = self.get_queryset().get(pk=pk)
            download_file = job.create_download_file(format)

            if download_file:
                return sendfile(request, download_file, attachment=True)
            else:
                return Response('PENDING')
        except QueryJob.DoesNotExist:
            raise Http404


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

    @list_route(methods=['get'], permission_classes=(IsAuthenticated, ))
    def user(self, request):
        examples = Example.objects.filter(groups__in=self.request.user.groups.all())
        serializer = UserExampleSerializer(examples, many=True)
        return Response(serializer.data)


class QueueViewSet(ChoicesViewSet):
    permission_classes = (IsAuthenticated, )
    queryset = settings.QUERY['queues']


class QueryLanguageViewSet(ChoicesViewSet):
    permission_classes = (IsAuthenticated, )
    queryset = settings.QUERY['query_languages']
