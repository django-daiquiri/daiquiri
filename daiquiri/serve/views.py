import io
import os
import zipfile

from sendfile import sendfile

from django.shortcuts import render
from django.http import HttpResponse, Http404

from daiquiri.core.adapter import get_adapter
from daiquiri.metadata.models import Database, Table, Directory
from daiquiri.query.models import QueryJob

from .utils import get_columns, get_column, normalize_file_path


def table(request, database_name, table_name):

    try:
        get_columns(request.user, database_name, table_name)
    except (QueryJob.DoesNotExist, Database.DoesNotExist, Table.DoesNotExist):
        raise Http404

    return render(request, 'serve/table.html', {
        'database': database_name,
        'table': table_name
    })


def files(request, file_path):

    directories = Directory.objects.filter_by_access_level(request.user)
    for directory in directories:
        file_path = normalize_file_path(directory.path, file_path)
        full_path = os.path.join(directory.path, file_path)

        if os.path.isfile(full_path):
            return sendfile(request, full_path, attachment=False)

    raise Http404


def archive(request):

    directories = Directory.objects.filter_by_access_level(request.user)

    database_name = request.GET.get('database')
    table_name = request.GET.get('table')
    column_name = request.GET.get('column')

    files = []

    if database_name and table_name and column_name:
        # get columns of this table the user is allowed to access
        column = get_column(request.user, database_name, table_name, column_name)
        if column:
            # get the filenames
            adapter = get_adapter()
            count = adapter.database.count_rows(database_name, table_name)
            rows = adapter.database.fetch_rows(database_name, table_name, [column['name']], page_size=count)

            for row in rows:
                for file_path in row:
                    for directory in directories:
                        file_path = normalize_file_path(directory.path, file_path)
                        if os.path.isfile(os.path.join(directory.path, file_path)):
                            files.append((directory.path, file_path))

    if files:
        f = io.BytesIO()
        with zipfile.ZipFile(f, 'w') as z:
            for directory_path, file_path in files:
                os.chdir(directory_path)
                z.write(file_path)

        return HttpResponse(f.getvalue(), content_type='application/zip')
    else:
        raise Http404
