import os
from mimetypes import guess_type
from sendfile import sendfile

from django.shortcuts import render
from django.http import Http404

from daiquiri.metadata.models import Database, Table, Directory
from daiquiri.query.models import QueryJob

from .utils import get_columns, get_full_path


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

    directories = Directory.objects.filter_by_access_level(request.user)
    for directory in directories:
        full_path = get_full_path(directory.path, file_path)

        if os.path.isfile(full_path):
            return sendfile(request, full_path, attachment=False)

    raise Http404
