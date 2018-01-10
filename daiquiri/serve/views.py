from django.shortcuts import render
from django.http import Http404

from .utils import get_columns


def table(request, database_name, table_name):

    columns = get_columns(request.user, database_name, table_name)

    if columns:
        return render(request, 'serve/table.html', {
            'database': database_name,
            'table': table_name
        })

    # if nothing worked, return 404
    raise Http404
