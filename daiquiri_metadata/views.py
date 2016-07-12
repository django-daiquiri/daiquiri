from django.contrib.auth.models import Group
from django.shortcuts import render

from rest_framework import viewsets, status
from rest_framework.response import Response

from daiquiri_core.serializers import ChoicesSerializer

from .models import *
from .serializers import *
from .utils import discover_tables, discover_columns


def metadata(request):
    return render(request, 'metadata/metadata.html', {})


class DatabaseViewSet(viewsets.ModelViewSet):
    queryset = Database.objects.all()

    def get_serializer_class(self):
        if self.request.GET.get('nested'):
            return NestedDatabaseSerializer
        else:
            return DatabaseSerializer

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        database = serializer.save()

        if request.data.get('discover'):
            for table_metadata in discover_tables(database.name):
                table_metadata['database'] = database.id
                table_metadata['groups'] = request.data['groups']

                table_serializer = TableSerializer(data=table_metadata)
                if table_serializer.is_valid():
                    table = table_serializer.save()

                    for column_metadata in discover_columns(database.name, table.name):
                        column_metadata['table'] = table.id
                        column_metadata['groups'] = request.data['groups']

                        column_serializer = ColumnSerializer(data=column_metadata)
                        if column_serializer.is_valid():
                            column_serializer.save()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class TableViewSet(viewsets.ModelViewSet):
    queryset = Table.objects.all()

    def get_serializer_class(self):
        if self.request.GET.get('nested'):
            return NestedTableSerializer
        else:
            return TableSerializer

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        table = serializer.save()

        if request.data.get('discover'):
            for column_metadata in discover_columns(table.database.name, table.name):
                column_metadata['table'] = table.id
                column_metadata['groups'] = request.data['groups']

                column_serializer = ColumnSerializer(data=column_metadata)
                if column_serializer.is_valid():
                    column_serializer.save()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


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
