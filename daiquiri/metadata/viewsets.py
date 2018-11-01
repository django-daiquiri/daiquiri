from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from rest_framework.decorators import list_route, detail_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, TokenAuthentication

from django_filters.rest_framework import DjangoFilterBackend

from daiquiri.core.adapter import DatabaseAdapter
from daiquiri.core.viewsets import ChoicesViewSet
from daiquiri.core.permissions import HasModelPermission
from daiquiri.core.constants import LICENSE_CHOICES, ACCESS_LEVEL_CHOICES

from .models import Schema, Table, Column, Function
from .serializers import (
    SchemaSerializer,
    TableSerializer,
    ColumnSerializer,
    FunctionSerializer
)
from .serializers.export import (
    SchemaSerializer as ExportSchemaSerializer,
    FunctionSerializer as ExportFunctionSerializer
)
from .serializers.management import (
    SchemaSerializer as ManagementSchemaSerializer,
    FunctionSerializer as ManagementFunctionSerializer
)
from .serializers.user import (
    SchemaSerializer as UserSchemaSerializer,
    FunctionSerializer as UserFunctionSerializer
)


class SchemaViewSet(viewsets.ModelViewSet):
    permission_classes = (HasModelPermission, )
    authentication_classes = (SessionAuthentication, TokenAuthentication)

    queryset = Schema.objects.all()
    serializer_class = SchemaSerializer

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filter_fields = ('name', 'access_level', 'metadata_access_level')
    search_fields = ('name', 'description')
    ordering_fields = ('name', 'access_level', 'metadata_access_level')

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        schema = serializer.save()

        if request.data.get('discover'):
            adapter = DatabaseAdapter()

            for table_metadata in adapter.fetch_tables(schema.name):
                table_metadata['schema'] = schema.id
                table_metadata['groups'] = [group.id for group in schema.groups.all()]
                for key in ['license', 'access_level', 'metadata_access_level']:
                    table_metadata[key] = getattr(schema, key)

                table_serializer = TableSerializer(data=table_metadata)
                if table_serializer.is_valid():
                    table = table_serializer.save()

                    for column_metadata in adapter.fetch_columns(schema.name, table.name):
                        column_metadata['table'] = table.id
                        column_metadata['groups'] = [group.id for group in table.groups.all()]
                        for key in ['access_level', 'metadata_access_level']:
                            column_metadata[key] = getattr(table, key)

                        column_serializer = ColumnSerializer(data=column_metadata)
                        if column_serializer.is_valid():
                            column_serializer.save()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @list_route()
    def management(self, request):
        queryset = Schema.objects.all()
        serializer = ManagementSchemaSerializer(queryset, many=True)
        return Response(serializer.data)

    @list_route(methods=['get'], permission_classes=[])
    def user(self, request):
        # filter the schemas which are published for the groups of the user
        queryset = Schema.objects.filter_by_access_level(self.request.user)
        serializer = UserSchemaSerializer(queryset, context={'request': request}, many=True)
        return Response(serializer.data)

    @list_route(methods=['get'], url_path='export', url_name='export-detail')
    def export_list(self, request):
        queryset = Schema.objects.all()
        serializer = ExportSchemaSerializer(queryset, many=True)
        return Response(serializer.data)

    @detail_route(methods=['get'], url_path='export', url_name='export-detail')
    def export_detail(self, request, pk=None):
        queryset = Schema.objects.get(pk=pk)
        serializer = ExportSchemaSerializer(queryset)
        return Response(serializer.data)


class TableViewSet(viewsets.ModelViewSet):
    permission_classes = (HasModelPermission, )
    authentication_classes = (SessionAuthentication, TokenAuthentication)

    queryset = Table.objects.all()
    serializer_class = TableSerializer

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filter_fields = ('name', 'access_level', 'metadata_access_level')
    search_fields = ('name', 'description')
    ordering_fields = ('name', 'access_level', 'metadata_access_level')

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        table = serializer.save()

        if request.data.get('discover'):
            adapter = DatabaseAdapter()

            for column_metadata in adapter.fetch_columns(table.schema.name, table.name):
                column_metadata['table'] = table.id
                column_metadata['groups'] = [group.id for group in table.groups.all()]
                for key in ['access_level', 'metadata_access_level']:
                    column_metadata[key] = getattr(table, key)

                column_serializer = ColumnSerializer(data=column_metadata)
                if column_serializer.is_valid():
                    column_serializer.save()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @list_route(methods=['get'])
    def discover(self, request):
        schema_name = request.GET.get('schema')
        table_name = request.GET.get('table')

        if schema_name and table_name:
            adapter = DatabaseAdapter()
            table_metadata = adapter.fetch_table(schema_name, table_name)
            table_metadata['nrows'] = adapter.fetch_nrows(schema_name, table_name)
            table_metadata['size'] = adapter.fetch_size(schema_name, table_name)
            return Response([table_metadata])
        else:
            return Response([])


class ColumnViewSet(viewsets.ModelViewSet):
    permission_classes = (HasModelPermission, )
    authentication_classes = (SessionAuthentication, TokenAuthentication)

    queryset = Column.objects.all()
    serializer_class = ColumnSerializer

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filter_fields = ('name', 'access_level', 'metadata_access_level')
    search_fields = ('name', 'description')
    ordering_fields = ('name', 'access_level', 'metadata_access_level')

    @list_route(methods=['get'])
    def discover(self, request):
        schema_name = request.GET.get('schema')
        table_name = request.GET.get('table')
        column_name = request.GET.get('column')

        if schema_name and table_name and column_name:
            return Response([DatabaseAdapter().fetch_column(schema_name, table_name, column_name)])
        else:
            return Response([])


class FunctionViewSet(viewsets.ModelViewSet):
    permission_classes = (HasModelPermission, )
    authentication_classes = (SessionAuthentication, TokenAuthentication)

    queryset = Function.objects.all()
    serializer_class = FunctionSerializer

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filter_fields = ('name', 'access_level', 'metadata_access_level')
    search_fields = ('name', 'description')
    ordering_fields = ('name', 'access_level', 'metadata_access_level')

    @list_route(methods=['get'])
    def management(self, request):
        queryset = Function.objects.all()
        serializer = ManagementFunctionSerializer(queryset, many=True)
        return Response(serializer.data)

    @list_route(methods=['get'])
    def export(self, request):
        queryset = Function.objects.all()
        serializer = ExportFunctionSerializer(queryset, many=True)
        return Response(serializer.data)

    @list_route(methods=['get'], permission_classes=[])
    def user(self, request):
        queryset = Function.objects.filter_by_access_level(self.request.user)
        serializer = UserFunctionSerializer(queryset, many=True)
        return Response(serializer.data)


class TableTypeViewSet(ChoicesViewSet):
    permission_classes = (IsAuthenticated, )
    authentication_classes = (SessionAuthentication, TokenAuthentication)

    queryset = Table.TYPE_CHOICES


class LicenseViewSet(ChoicesViewSet):
    permission_classes = (IsAuthenticated, )
    authentication_classes = (SessionAuthentication, TokenAuthentication)

    queryset = LICENSE_CHOICES


class AccessLevelViewSet(ChoicesViewSet):
    permission_classes = (IsAuthenticated, )
    authentication_classes = (SessionAuthentication, TokenAuthentication)

    queryset = ACCESS_LEVEL_CHOICES
