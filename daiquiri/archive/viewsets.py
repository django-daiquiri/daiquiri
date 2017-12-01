from collections import OrderedDict

from django.conf import settings

from rest_framework import viewsets
from rest_framework.response import Response

from daiquiri.core.viewsets import RowViewSet as BaseRowViewSet
from daiquiri.core.adapter import get_adapter


class RowViewSet(BaseRowViewSet):

    def list(self, request, *args, **kwargs):

        adapter = get_adapter()

        database_name = settings.ARCHIVE_DATABASE
        table_name = settings.ARCHIVE_TABLE
        column_names = [column['name'] for column in settings.ARCHIVE_COLUMNS]

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

        # query the database for the total number of rows
        count = adapter.database.count_rows(database_name, table_name, column_names, search, filters)

        # # query the paginated rowset
        results = adapter.database.fetch_rows(database_name, table_name, column_names, ordering, page, page_size, search, filters)

        # get the previous and next url
        next = self._get_next_url(page, page_size, count)
        previous = self._get_previous_url(page)

        return Response(OrderedDict((
            ('count', count),
            ('next', next),
            ('previous', previous),
            ('results', results)
        )))


class ColumnViewSet(viewsets.ViewSet):

    def list(self, request, *args, **kwargs):

        return Response(settings.ARCHIVE_COLUMNS)
