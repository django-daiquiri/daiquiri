from collections import OrderedDict

from django.shortcuts import redirect

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

from daiquiri.core.viewsets import RowViewSetMixin
from daiquiri.core.adapter import DatabaseAdapter

from .serializers import ColumnSerializer
from .utils import get_columns, get_resolver


class RowViewSet(RowViewSetMixin, viewsets.GenericViewSet):

    def list(self, request, *args, **kwargs):

        # get schema, table and column_names from the querystring
        schema_name = self.request.GET.get('schema')
        table_name = self.request.GET.get('table')
        column_names = self.request.GET.getlist('column')

        # get the columns using the utils function
        columns = get_columns(self.request.user, schema_name, table_name, column_names)

        if columns:
            # get column names from the checked columns (again)
            column_names = [column.name for column in columns]

            # get the row query params from the request
            ordering, page, page_size, search, filters = self._get_query_params(column_names)

            # get database adapter
            adapter = DatabaseAdapter()

            # query the database for the total number of rows
            count = adapter.count_rows(schema_name, table_name, column_names, search, filters)

            # query the paginated rowset
            results = adapter.fetch_rows(schema_name, table_name, column_names, ordering, page, page_size, search, filters)

            # return ordered dict to be send as json
            return Response(OrderedDict((
                ('count', count),
                ('results', results),
                ('next', self._get_next_url(page, page_size, count)),
                ('previous', self._get_previous_url(page))
            )))

        # if nothing worked, return 404
        raise NotFound()


class ColumnViewSet(viewsets.ViewSet):

    def list(self, request, *args, **kwargs):

        # get database, table and column_names from the querystring
        schema_name = self.request.GET.get('schema')
        table_name = self.request.GET.get('table')
        column_names = self.request.GET.getlist('column')

        # get the columns using the utils function
        columns = get_columns(self.request.user, schema_name, table_name, column_names)

        if columns:
            # get column names from the checked columns (again)
            columns = [column for column in columns if column.name in column_names]

            return Response(ColumnSerializer(columns, many=True).data)

        # if nothing worked, return 404
        raise NotFound()


class ReferenceViewSet(viewsets.ViewSet):

    def list(self, request):

        key = request.GET.get('key', None)
        value = request.GET.get('value', None)

        resolver = get_resolver()
        if resolver is None:
            raise NotFound()

        url = resolver.resolve(key, value)
        if url is None:
            raise NotFound()

        return redirect(url)
