from django.contrib.auth.models import Group
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import list_route

from daiquiri_core.adapter import get_adapter
from daiquiri_core.serializers import ChoicesSerializer

from .models import *
from .serializers import *


def metadata(request):
    return render(request, 'metadata/metadata.html', {})


class DatabaseViewSet(viewsets.ModelViewSet):
    queryset = Database.objects.all()
    serializer_class = DatabaseSerializer

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        database = serializer.save()

        if request.data.get('discover'):
            adapter = get_adapter('metadata')

            for table_metadata in adapter.fetch_tables(database.name):
                table_metadata['database'] = database.id
                table_metadata['groups'] = request.data['groups']

                table_serializer = TableSerializer(data=table_metadata)
                if table_serializer.is_valid():
                    table = table_serializer.save()

                    for column_metadata in adapter.fetch_columns(database.name, table.name):
                        column_metadata['table'] = table.id
                        column_metadata['groups'] = request.data['groups']

                        column_serializer = ColumnSerializer(data=column_metadata)
                        if column_serializer.is_valid():
                            column_serializer.save()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @list_route()
    def nested(self, request):
        queryset = Database.objects.all()
        serializer = NestedDatabaseSerializer(queryset, many=True)
        return Response(serializer.data)


class TableViewSet(viewsets.ModelViewSet):
    queryset = Table.objects.all()
    serializer_class = TableSerializer

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        table = serializer.save()

        if request.data.get('discover'):
            adapter = get_adapter('metadata')

            for column_metadata in adapter.fetch_columns(table.database.name, table.name):
                column_metadata['table'] = table.id
                column_metadata['groups'] = request.data['groups']

                column_serializer = ColumnSerializer(data=column_metadata)
                if column_serializer.is_valid():
                    column_serializer.save()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @list_route(methods=['get'], permission_classes=[])
    def discover(self, request):
        database_name = request.GET.get('database')
        table_name = request.GET.get('table')

        if database_name and table_name:
            return Response([get_adapter('metadata').fetch_table(database_name, table_name)])
        else:
            return Response([])

    @list_route()
    def nested(self, request):
        queryset = Table.objects.all()
        serializer = NestedTableSerializer(queryset, many=True)
        return Response(serializer.data)


class ColumnViewSet(viewsets.ModelViewSet):
    queryset = Column.objects.all()
    serializer_class = ColumnSerializer

    @list_route(methods=['get'], permission_classes=[])
    def discover(self, request):
        database_name = request.GET.get('database')
        table_name = request.GET.get('table')
        column_name = request.GET.get('column')

        if database_name and table_name:
            return Response([get_adapter('metadata').fetch_column(database_name, table_name, column_name)])
        else:
            return Response([])

    @list_route()
    def nested(self, request):
        queryset = Column.objects.all()
        serializer = NestedColumnSerializer(queryset, many=True)
        return Response(serializer.data)


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


def dbview(request, dbname):

    try:
        db = Database.objects.get(name=dbname)
        db_tables =  list(Table.objects.filter(database=db.id))
        print (db_tables)
        db_view = {
            'db_name': db.name,
            'db_description': db.description,
            'db_tables': db_tables
        }
        return render(request, "metadata/database_view.html", db_view)

    except ObjectDoesNotExist:
        raise Http404


def tableview(request, dbname, tablename):

    try:
        dbid = Database.objects.get(name=dbname).id
        the_table = Table.objects.filter(name=tablename).get(database=dbid)
        full_table_name = dbname + '.' + tablename
        table_view = {
            'full_table_name': full_table_name,
            'table_name': the_table.name,
            'table_description': the_table.description,
            'db_name': dbname
        }
        return render(request, "metadata/table_view.html", table_view)

    except ObjectDoesNotExist:
        raise Http404


