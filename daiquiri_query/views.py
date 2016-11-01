from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.timezone import now

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from daiquiri_metadata.models import Database, Function

from .models import *
from .serializers import *
from .exceptions import *


@login_required()
def query(request):
    return render(request, 'query/query.html', {})


class QueryJobViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        return QueryJob.objects.filter(owner=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return QueryJobListSerializer
        elif self.action == 'retrieve':
            return QueryJobRetrieveSerializer
        elif self.action == 'create':
            return QueryJobCreateSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return QueryJobUpdateSerializer

    def perform_create(self, serializer):
        if 'table_name' in serializer.data:
            table_name = serializer.data['table_name']
        else:
            table_name = now().strftime("%Y-%m-%d-%H-%M-%S")

        try:
            QueryJob.submission.submit(
                serializer.data['query_language'],
                serializer.data['query'],
                serializer.data['queue'],
                table_name,
                self.request.user
            )
        except ADQLSyntaxError as e:
            raise ValidationError({'query': e.message})
        except MySQLSyntaxError as e:
            raise ValidationError({'query': e.message})
        except PermissionError as e:
            raise ValidationError({'query': e.message})
        except TableError as e:
            raise ValidationError({'table_name': e.message})

    def perform_update(self, serializer):
        serializer.save()

    def perform_destroy(self, instance):
        instance.archive()


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
