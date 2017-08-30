from sendfile import sendfile

from django.shortcuts import render
from django.http import Http404

from daiquiri.metadata.models import Database, Table
from daiquiri.query.models import QueryJob

from .utils import get_columns


def serve_table(request, database_name, table_name):

    try:
        get_columns(request.user, database_name, table_name)
    except (QueryJob.DoesNotExist, Database.DoesNotExist, Table.DoesNotExist):
        raise Http404

    return render(request, 'serve/serve_table.html', {
        'database': database_name,
        'table': table_name
    })


def files(request, file_path):
    absolute_path = file_path

    return sendfile(request, absolute_path, attachment=True)
