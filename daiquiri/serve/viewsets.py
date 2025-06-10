from collections import OrderedDict

from rest_framework import viewsets
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from daiquiri.core.adapter import DatabaseAdapter
from daiquiri.core.utils import fix_for_json
from daiquiri.core.viewsets import RowViewSetMixin
from daiquiri.metadata.utils import get_user_columns

from .serializers import ColumnSerializer


class RowViewSet(RowViewSetMixin, viewsets.GenericViewSet):

    def list(self, request, *args, **kwargs):

        # get schema, table and column_names from the querystring
        schema_name = self.request.GET.get('schema')
        table_name = self.request.GET.get('table')
        column_names = self.request.GET.getlist('column')

        # get the table column names
        user_columns = get_user_columns(self.request.user, schema_name, table_name)

        if user_columns:
            # get the row query params from the request
            ordering, page, page_size, search, filters = self._get_query_params(user_columns)

            # filter by the input column names
            if column_names:
                column_names = [column.name for column in user_columns if column.name in column_names]
            else:
                column_names = [column.name for column in user_columns]

            # get database adapter
            adapter = DatabaseAdapter()

            # query the database for the total number of rows
            count = adapter.count_rows(schema_name, table_name, column_names, search, filters)

            # query the paginated rowset
            results = adapter.fetch_rows(schema_name, table_name, column_names,
                                         ordering, page, page_size, search, filters)

            # return ordered dict to be send as json
            return Response(OrderedDict((
                ('count', count),
                ('results', fix_for_json(results)),
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

        # get the table column names
        user_columns = get_user_columns(self.request.user, schema_name, table_name)

        if user_columns:
            
            if column_names:
                columns = [column for column in user_columns if column.name in column_names]
            else:
                columns = list(user_columns)

            return Response(ColumnSerializer(columns, many=True).data)

        # if nothing worked, return 404
        raise NotFound()
