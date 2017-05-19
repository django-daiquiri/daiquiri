from collections import OrderedDict

from django.shortcuts import render
from django.http import Http404

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.exceptions import ParseError, NotFound
from rest_framework.reverse import reverse

from daiquiri.core.adapter import get_adapter

from daiquiri.metadata.models import Database, Table, Column
from daiquiri.query.utils import get_user_database_name

from .serializers import *


def serve_table(request, database_name, table_name):

    # check permission on database
    database = Database.permissions.get(request.user, database_name=database_name)
    table = Table.permissions.get(request.user, database=database, table_name=table_name)

    if not (database or table):
        raise Http404()
    else:
        return render(request, 'serve/serve_table.html', {
            'database': database_name,
            'table': table_name
        })


class RowViewSet(viewsets.ViewSet):

    def list(self, request, *args, **kwargs):

        # get database and table from the querystring
        database_name = self.request.GET.get('database')
        table_name = self.request.GET.get('table')

        # get the ordering
        ordering = self.request.GET.get('ordering')

        # get the search string
        filter_string = self.request.GET.get('filter')

        # get the page from the querystring and make sure it is an int
        page = self._get_page()

        # get the page_size from the querystring and make sure it is an int
        page_size = self._get_page_size()

        # get database adapter
        adapter = get_adapter('data')

        # get query backend adapter
        user_database_name = get_user_database_name(self.request.user.username)

        if database_name == user_database_name:
            # get database adapter and fetch the columns
            columns = adapter.fetch_columns(database_name, table_name)
            column_names = [column['name'] for column in columns]
        else:
            # check permissions on the database
            database = Database.permissions.get(self.request.user, database_name=database_name)
            if not database:
                raise NotFound()

            # check permissions on the table
            table = Table.permissions.get(self.request.user, database=database, table_name=table_name)
            if not table:
                raise NotFound()

            # get columns for this table
            columns = Column.permissions.all(self.request.user, table=table)
            column_names = [column.name for column in columns]

        # query the database for the total number of rows
        count = adapter.count_rows(database_name, table_name, column_names, filter_string)

        # query the paginated rowset
        results = adapter.fetch_rows(database_name, table_name, column_names, ordering, page, page_size, filter_string)

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

        # get database adapter
        user_database_name = get_user_database_name(self.request.user.username)

        if database_name == user_database_name:
            # get database adapter and fetch the columns
            columns = get_adapter('data').fetch_columns(database_name, table_name)
        else:
            # check permissions on the database
            database = Database.permissions.get(self.request.user, database_name=database_name)
            if not database:
                raise NotFound()

            # check permissions on the table
            table = Table.permissions.get(self.request.user, database=database, table_name=table_name)
            if not table:
                raise NotFound()

            # get columns for this table
            columns = Column.permissions.all(self.request.user, table=table)

        return Response(ColumnSerializer(columns, many=True).data)
