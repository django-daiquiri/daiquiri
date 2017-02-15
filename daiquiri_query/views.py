import json
from sendfile import sendfile

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.http import Http404
from django.shortcuts import render
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import detail_route

from daiquiri_core.utils import human2bytes
from daiquiri_metadata.models import Database, Function
from daiquiri_uws.settings import PHASE_ARCHIVED

from .models import *
from .backends import get_query_backend
from .serializers import (
    FormSerializer,
    DropdownSerializer,
    QueryJobListSerializer,
    QueryJobRetrieveSerializer,
    QueryJobCreateSerializer,
    QueryJobUpdateSerializer,
    ExampleSerializer,
    DatabaseSerializer,
    FunctionSerializer
)
from .exceptions import (
    ADQLSyntaxError,
    MySQLSyntaxError,
    PermissionError,
    TableError,
    ConnectionError
)


@login_required()
def query(request):
    return render(request, 'query/query.html', {
        'query_settings': settings.QUERY
    })

class StatusViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        return []

    def list(self, request):

        quota = 0
        for group in request.user.groups.all():
            group_quota = human2bytes(settings.QUERY['quota'][group.name])
            quota = group_quota if group_quota > quota else quota

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
        elif self.action == 'retrieve':
            return QueryJobRetrieveSerializer
        elif self.action == 'create':
            return QueryJobCreateSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return QueryJobUpdateSerializer

    def list(self, request, *args, **kwargs):
        query_backend = get_query_backend()
        user_database_name = query_backend.get_user_database_name(self.request.user.username)

        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data

        for job in data:
            job['columns'] = query_backend.fetch_columns(user_database_name, job['table_name'])

        return Response(data)

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
            QueryJob.objects.submit(
                serializer.data['query_language'],
                serializer.data['query'],
                serializer.data['queue'],
                table_name,
                self.request.user
            )
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


class ExampleViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (IsAuthenticated, )

    serializer_class = ExampleSerializer

    def get_queryset(self):
        return Example.objects.filter(groups__in=self.request.user.groups.all())


class DatabaseViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (IsAuthenticated, )

    serializer_class = DatabaseSerializer

    def get_queryset(self):
        return Database.objects.filter(groups__in=self.request.user.groups.all())


class FunctionViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (IsAuthenticated, )

    serializer_class = FunctionSerializer

    def get_queryset(self):
        return Function.objects.filter(groups__in=self.request.user.groups.all())
