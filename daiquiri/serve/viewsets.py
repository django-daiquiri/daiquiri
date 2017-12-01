from collections import OrderedDict

from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound

from daiquiri.core.viewsets import RowViewSet as BaseRowViewSet
from daiquiri.core.adapter import get_adapter

from .serializers import ColumnSerializer
from .utils import get_columns, get_resolver


class RowViewSet(BaseRowViewSet):

    def list(self, request, *args, **kwargs):

        # get database and table from the querystring
        database_name = self.request.GET.get('database')
        table_name = self.request.GET.get('table')
        column_names = self.request.GET.getlist('column')

        # get the ordering
        ordering = self.request.GET.get('ordering')

        # get the search string
        search = self.request.GET.get('search')

        # get additional filters from the querystring
        filters = self._get_filters()

        # get the page from the querystring and make sure it is an int
        page = self._get_page()

        # get the page_size from the querystring and make sure it is an int
        page_size = self._get_page_size()

        # get the columns using the utils function
        columns = get_columns(self.request.user, database_name, table_name)

        # check
        if search and filters:
            raise ValidationError(_('Filtering by \'search=value\' and \'column_name=value\' is mutually exclusive.'))

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
            count = adapter.database.count_rows(database_name, table_name, column_names, search, filters)

            # query the paginated rowset
            results = adapter.database.fetch_rows(database_name, table_name, column_names, ordering, page, page_size, search, filters)

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
