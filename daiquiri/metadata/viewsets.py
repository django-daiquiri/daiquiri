from django.conf import settings
from django.db.models import Max

from rest_framework import filters, status, viewsets
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend

from daiquiri.core.adapter import DatabaseAdapter
from daiquiri.core.constants import ACCESS_LEVEL_CHOICES
from daiquiri.core.permissions import HasModelPermission
from daiquiri.core.utils import get_model_field_meta
from daiquiri.core.viewsets import ChoicesViewSet

from .models import Column, Function, Schema, Table
from .serializers import ColumnSerializer, FunctionSerializer, SchemaSerializer, TableSerializer
from .serializers.export import FunctionSerializer as ExportFunctionSerializer
from .serializers.export import SchemaSerializer as ExportSchemaSerializer
from .serializers.management import FunctionSerializer as ManagementFunctionSerializer
from .serializers.management import SchemaSerializer as ManagementSchemaSerializer
from .serializers.user import FunctionSerializer as UserFunctionSerializer
from .serializers.user import SchemaSerializer as UserSchemaSerializer


class SchemaViewSet(viewsets.ModelViewSet):
    permission_classes = (HasModelPermission, )
    authentication_classes = (SessionAuthentication, TokenAuthentication)

    queryset = Schema.objects.all()
    serializer_class = SchemaSerializer

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ('name', 'access_level', 'metadata_access_level')
    search_fields = ('name', 'description')
    ordering_fields = ('name', 'access_level', 'metadata_access_level')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        schema = serializer.save()
        schema.order = (Schema.objects.aggregate(order=Max('order'))['order'] or 0) + 1
        schema.save()

        if request.data.get('discover'):
            adapter = DatabaseAdapter()

            for table_order, table_metadata in enumerate(adapter.fetch_tables(schema.name)):
                table_metadata['order'] = table_order
                table_metadata['schema'] = schema.id
                table_metadata['groups'] = [group.id for group in schema.groups.all()]
                for key in ['license', 'access_level', 'metadata_access_level']:
                    table_metadata[key] = getattr(schema, key)

                table_serializer = TableSerializer(data=table_metadata)
                if table_serializer.is_valid():
                    table = table_serializer.save()
                    table.discover(adapter)
                    table.save()

                    for column_order, column_metadata in enumerate(adapter.fetch_columns(schema.name, table.name)):
                        column_metadata['order'] = column_order
                        column_metadata['table'] = table.id
                        column_metadata['groups'] = [group.id for group in table.groups.all()]
                        for key in ['access_level', 'metadata_access_level']:
                            column_metadata[key] = getattr(table, key)

                        column_serializer = ColumnSerializer(data=column_metadata)
                        if column_serializer.is_valid():
                            column = column_serializer.save()
                            column.discover(adapter)
                            column.save()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False)
    def management(self, request):
        queryset = Schema.objects.all()
        serializer = ManagementSchemaSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[])
    def user(self, request):
        # filter the schemas which are published for the groups of the user
        queryset = Schema.objects.filter_by_access_level(self.request.user)
        serializer = UserSchemaSerializer(queryset, context={'request': request}, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='export', url_name='export-detail')
    def export_list(self, request):
        queryset = Schema.objects.all()
        serializer = ExportSchemaSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='export', url_name='export-detail')
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
    filterset_fields = ('name', 'access_level', 'metadata_access_level')
    search_fields = ('name', 'description')
    ordering_fields = ('name', 'access_level', 'metadata_access_level')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        table = serializer.save()
        table.order = (table.schema.tables.aggregate(order=Max('order'))['order'] or 0) + 1
        table.save()

        if request.data.get('discover'):
            adapter = DatabaseAdapter()
            table.discover(adapter)
            table.save()

            for column_order, column_metadata in enumerate(adapter.fetch_columns(table.schema.name, table.name)):
                column_metadata['order'] = column_order
                column_metadata['table'] = table.id
                column_metadata['groups'] = [group.id for group in table.groups.all()]
                for key in ['access_level', 'metadata_access_level']:
                    column_metadata[key] = getattr(table, key)

                column_serializer = ColumnSerializer(data=column_metadata)
                if column_serializer.is_valid():
                    column = column_serializer.save()
                    column.discover(adapter)
                    column.save()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['post'])
    def discover(self, request, pk=None):
        adapter = DatabaseAdapter()
        table = self.get_object()
        table.discover(adapter)
        table.save()
        return Response(self.get_serializer(table).data)


class ColumnViewSet(viewsets.ModelViewSet):
    permission_classes = (HasModelPermission, )
    authentication_classes = (SessionAuthentication, TokenAuthentication)

    queryset = Column.objects.all()
    serializer_class = ColumnSerializer

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ('name', 'access_level', 'metadata_access_level')
    search_fields = ('name', 'description')
    ordering_fields = ('name', 'access_level', 'metadata_access_level')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        column = serializer.save()
        column.order = (column.table.columns.aggregate(order=Max('order'))['order'] or 0) + 1
        column.save()

        if request.data.get('discover'):
            adapter = DatabaseAdapter()
            column.discover(adapter)
            column.save()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['post'])
    def discover(self, request, pk=None):
        adapter = DatabaseAdapter()
        column = self.get_object()
        column.discover(adapter)
        column.save()
        return Response(self.get_serializer(column).data)


class FunctionViewSet(viewsets.ModelViewSet):
    permission_classes = (HasModelPermission, )
    authentication_classes = (SessionAuthentication, TokenAuthentication)

    queryset = Function.objects.all()
    serializer_class = FunctionSerializer

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ('name', 'access_level', 'metadata_access_level')
    search_fields = ('name', 'description')
    ordering_fields = ('name', 'access_level', 'metadata_access_level')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        function = serializer.save()
        function.order = (Function.objects.aggregate(order=Max('order'))['order'] or 0) + 1
        function.save()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=['get'])
    def management(self, request):
        queryset = Function.objects.all()
        serializer = ManagementFunctionSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def export(self, request):
        queryset = Function.objects.all()
        serializer = ExportFunctionSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[])
    def user(self, request):
        queryset = Function.objects.filter_by_access_level(self.request.user)
        serializer = UserFunctionSerializer(queryset, many=True)
        return Response(serializer.data)


class LicenseViewSet(ChoicesViewSet):
    permission_classes = (IsAuthenticated, )
    authentication_classes = (SessionAuthentication, TokenAuthentication)

    queryset = settings.LICENSE_CHOICES


class AccessLevelViewSet(ChoicesViewSet):
    permission_classes = (IsAuthenticated, )
    authentication_classes = (SessionAuthentication, TokenAuthentication)

    queryset = ACCESS_LEVEL_CHOICES


class MetaViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated, )
    authentication_classes = (SessionAuthentication, TokenAuthentication)

    def list(self, request, *args, **kwargs):
        return Response(get_model_field_meta(Schema, Table, Column, Function))
