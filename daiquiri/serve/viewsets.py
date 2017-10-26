from collections import OrderedDict

from django.utils.translation import ugettext_lazy as _

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, ParseError, NotFound
from rest_framework.reverse import reverse

from daiquiri.core.adapter import get_adapter

from .serializers import ColumnSerializer
from .utils import get_columns


class RowViewSet(viewsets.ViewSet):

    def list(self, request, *args, **kwargs):

        # get database and table from the querystring
        database_name = self.request.GET.get('database')
        table_name = self.request.GET.get('table')
        column_names = self.request.GET.getlist('column')

        # get the ordering
        ordering = self.request.GET.get('ordering')

        # get the search string
        filter_string = self.request.GET.get('filter')

        # get additional filters from the querystring
        filters = self._get_filters()

        # get the page from the querystring and make sure it is an int
        page = self._get_page()

        # get the page_size from the querystring and make sure it is an int
        page_size = self._get_page_size()

        # get the columns using the utils function
        columns = get_columns(self.request.user, database_name, table_name)

        # check
        if filter_string and filters:
            raise ValidationError(_('Filtering by \'filter=filter_string\' and \'column_name=value\' is mutually exclusive.'))

        if filters:
            for column_name in filters:
                if column_name not in [column['name'] for column in columns]:
                    raise ValidationError({
                            column_name: _('Column not found.')
                        })

        if columns:
            if column_names:
                column_names = [column['name'] for column in columns if column['name'] in column_names]
            else:
                column_names = [column['name'] for column in columns]

            # get database adapter
            adapter = get_adapter()

            # query the database for the total number of rows
            count = adapter.database.count_rows(database_name, table_name, column_names, filter_string, filters)

            # query the paginated rowset
            results = adapter.database.fetch_rows(database_name, table_name, column_names, ordering, page, page_size, filter_string, filters)

            # flatten the list if only one column is retrieved
            if len(column_names) == 1:
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

    def _get_filters(self):
        filters = {}
        for key, value in self.request.GET.items():
            if key not in ['database', 'table', 'column', 'ordering', 'filter', 'page', 'page_size']:
                filters[key] = value
        return filters

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
        column_names = self.request.GET.getlist('column')

        # get the columns using the utils function
        columns = get_columns(self.request.user, database_name, table_name)

        if columns:
            if column_names:
                columns = [column for column in columns if column['name'] in column_names]

            return Response(ColumnSerializer(columns, many=True).data)

        # if nothing worked, return 404
        raise NotFound()
