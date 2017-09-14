from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from rest_framework.decorators import list_route
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, TokenAuthentication

from daiquiri.core.adapter import get_adapter
from daiquiri.core.viewsets import ChoicesViewSet
from daiquiri.core.permissions import HasModelPermission
from daiquiri.core.constants import LICENSE_CHOICES, ACCESS_LEVEL_CHOICES

from .models import Database, Table, Column, Function
from .serializers import (
    DatabaseSerializer,
    TableSerializer,
    ColumnSerializer,
    FunctionSerializer
)
from .serializers.management import (
    DatabaseSerializer as ManagementDatabaseSerializer,
    FunctionSerializer as ManagementFunctionSerializer
)
from .serializers.user import (
    DatabaseSerializer as UserDatabaseSerializer,
    FunctionSerializer as UserFunctionSerializer
)


class DatabaseViewSet(viewsets.ModelViewSet):
    permission_classes = (HasModelPermission, )
    authentication_classes = (SessionAuthentication, TokenAuthentication)

    queryset = Database.objects.all()
    serializer_class = DatabaseSerializer

    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filter_fields = ('name', 'access_level', 'metadata_access_level')
    search_fields = ('name', 'description')
    ordering_fields = ('name', 'access_level', 'metadata_access_level')

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        database = serializer.save()

        if request.data.get('discover'):
            adapter = get_adapter()

            for table_metadata in adapter.database.fetch_tables(database.name):
                table_metadata['database'] = database.id
                table_metadata['groups'] = [group.id for group in database.groups.all()]
                for key in ['license', 'access_level', 'metadata_access_level']:
                    table_metadata[key] = getattr(database, key)

                table_serializer = TableSerializer(data=table_metadata)
                if table_serializer.is_valid():
                    table = table_serializer.save()

                    for column_metadata in adapter.database.fetch_columns(database.name, table.name):
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
        queryset = Database.objects.all()
        serializer = ManagementDatabaseSerializer(queryset, many=True)
        return Response(serializer.data)

    @list_route(methods=['get'], permission_classes=[])
    def user(self, request):
        # filter the databases which are published for the groups of the user
        queryset = Database.objects.filter_by_access_level(self.request.user)
        serializer = UserDatabaseSerializer(queryset, context={'request': request}, many=True)
        return Response(serializer.data)


class TableViewSet(viewsets.ModelViewSet):
    permission_classes = (HasModelPermission, )
    authentication_classes = (SessionAuthentication, TokenAuthentication)

    queryset = Table.objects.all()
    serializer_class = TableSerializer

    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filter_fields = ('name', 'access_level', 'metadata_access_level')
    search_fields = ('name', 'description')
    ordering_fields = ('name', 'access_level', 'metadata_access_level')

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        table = serializer.save()

        if request.data.get('discover'):
            adapter = get_adapter()

            for column_metadata in adapter.database.fetch_columns(table.database.name, table.name):
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
        database_name = request.GET.get('database')
        table_name = request.GET.get('table')

        if database_name and table_name:
            return Response([get_adapter().database.fetch_table(database_name, table_name)])
        else:
            return Response([])


class ColumnViewSet(viewsets.ModelViewSet):
    permission_classes = (HasModelPermission, )
    authentication_classes = (SessionAuthentication, TokenAuthentication)

    queryset = Column.objects.all()
    serializer_class = ColumnSerializer

    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filter_fields = ('name', 'access_level', 'metadata_access_level')
    search_fields = ('name', 'description')
    ordering_fields = ('name', 'access_level', 'metadata_access_level')

    @list_route(methods=['get'])
    def discover(self, request):
        database_name = request.GET.get('database')
        table_name = request.GET.get('table')
        column_name = request.GET.get('column')

        if database_name and table_name:
            return Response([get_adapter().database.fetch_column(database_name, table_name, column_name)])
        else:
            return Response([])


class FunctionViewSet(viewsets.ModelViewSet):
    permission_classes = (HasModelPermission, )
    authentication_classes = (SessionAuthentication, TokenAuthentication)

    queryset = Function.objects.all()
    serializer_class = FunctionSerializer

    filter_backends = (filters.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filter_fields = ('name', 'access_level', 'metadata_access_level')
    search_fields = ('name', 'description')
    ordering_fields = ('name', 'access_level', 'metadata_access_level')

    @list_route(methods=['get'])
    def management(self, request):
        queryset = Function.objects.all()
        serializer = ManagementFunctionSerializer(queryset, many=True)
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
