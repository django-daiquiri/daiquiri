from django.contrib.auth.models import Group
from django.shortcuts import render

from rest_framework import viewsets

from daiquiri_core.serializers import ChoicesSerializer

from .models import *
from .serializers import *


def metadata(request):
    return render(request, 'metadata/metadata.html', {})


class DatabaseViewSet(viewsets.ModelViewSet):
    queryset = Database.objects.all()

    def get_serializer_class(self):
        if self.request.GET.get('nested'):
            return NestedDatabaseSerializer
        else:
            return DatabaseSerializer


class TableViewSet(viewsets.ModelViewSet):
    queryset = Table.objects.all()

    def get_serializer_class(self):
        if self.request.GET.get('nested'):
            return NestedTableSerializer
        else:
            return TableSerializer


class ColumnViewSet(viewsets.ModelViewSet):
    queryset = Column.objects.all()

    def get_serializer_class(self):
        if self.request.GET.get('nested'):
            return NestedColumnSerializer
        else:
            return ColumnSerializer


class FunctionViewSet(viewsets.ModelViewSet):
    queryset = Function.objects.all()

    def get_serializer_class(self):
        if self.request.GET.get('nested'):
            return NestedFunctionSerializer
        else:
            return FunctionSerializer


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class TableTypeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ChoicesSerializer

    def get_queryset(self):
        return Table.TYPE_CHOICES
