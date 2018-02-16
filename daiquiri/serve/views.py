from django.shortcuts import render
from django.http import Http404

from .utils import get_columns


def table(request, schema_name, table_name):

    columns = get_columns(request.user, schema_name, table_name)

    if columns:
        return render(request, 'serve/table.html', {
            'schema': schema_name,
            'table': table_name
        })

    # if nothing worked, return 404
    raise Http404
