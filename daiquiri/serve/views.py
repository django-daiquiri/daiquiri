from django.shortcuts import render
from django.http import Http404

from daiquiri.metadata.models import Database, Table


def serve_table(request, database_name, table_name):

    # check permission on database
    database = Database.objects.filter_by_access_level(request.user).get(name=database_name)
    table = Table.objects.filter_by_access_level(request.user).filter(database=database).get(name=table_name)

    if not (database or table):
        raise Http404()
    else:
        return render(request, 'serve/serve_table.html', {
            'database': database_name,
            'table': table_name
        })
