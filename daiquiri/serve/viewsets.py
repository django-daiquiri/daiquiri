from collections import OrderedDict

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.exceptions import ParseError, NotFound
from rest_framework.reverse import reverse

from daiquiri.core.adapter import get_adapter

from .serializers import ColumnSerializer
from .utils import get_columns


class RowViewSet(viewsets.ViewSet):

    def list(self, request, *args, **kwargs):

        # get database and table from the querystring
        database_name = self.request.GET.get('database')
        table_name = self.request.GET.get('table')
        column_name = self.request.GET.get('column')

        # get the ordering
        ordering = self.request.GET.get('ordering')

        # get the search string
        filter_string = self.request.GET.get('filter')

        # get the page from the querystring and make sure it is an int
        page = self._get_page()

        # get the page_size from the querystring and make sure it is an int
        page_size = self._get_page_size()

        # get the columns using the utils function
        columns = get_columns(self.request.user, database_name, table_name)

        if columns:
            column_names = [column['name'] for column in columns]

            if column_name:
                if column_name not in column_names:
                    raise NotFound()
                else:
                    column_names = [column_name]

            # get database adapter
            adapter = get_adapter()

            # query the database for the total number of rows
            count = adapter.database.count_rows(database_name, table_name, column_names, filter_string)

            # query the paginated rowset
            results = adapter.database.fetch_rows(database_name, table_name, column_names, ordering, page, page_size, filter_string)

            # flatten the list if only one column is retrieved
            if column_name:
                results = [element for row in results for element in row]

            # get the previous and next url
            next = self._get_next_url(page, page_size, count)
            previous = self._get_previous_url(page)

            # return ordered dict to be send as json
            return Response(OrderedDict((
                ('count', count),
                ('next', next),
                ('previous', previous),
                ('results', results)
            )))

        # if nothing worked, return 404
        raise NotFound()

    def _get_page(self):
        try:
            return int(self.request.GET.get('page', '1'))
        except ValueError:
            raise ParseError('page must be an integer')

    def _get_page_size(self):
        try:
            return int(self.request.GET.get('page_size', '10'))
        except ValueError:
            raise ParseError('page_size must be an integer')

    def _get_next_url(self, page, page_size, count):
        url = reverse('serve:row-list', request=self.request)
        querydict = self.request.GET.copy()

        if page * page_size < count:
            querydict['page'] = page + 1
            return url + '?' + querydict.urlencode()
        else:
            return None

    def _get_previous_url(self, page):
        url = reverse('serve:row-list', request=self.request)
        querydict = self.request.GET.copy()

        if page > 1:
            querydict['page'] = page - 1
            return url + '?' + querydict.urlencode()
        else:
            return None


class ColumnViewSet(viewsets.ViewSet):

    def list(self, request, *args, **kwargs):

        # get database and table from the querystring
        database_name = self.request.GET.get('database')
        table_name = self.request.GET.get('table')

        # get the columns using the utils function
        columns = get_columns(self.request.user, database_name, table_name)

        if columns:
            return Response(ColumnSerializer(columns, many=True).data)

        # if nothing worked, return 404
        raise NotFound()
