from django.shortcuts import render
from django.shortcuts import get_object_or_404

from .models import Database, Table


def management(request):
    return render(request, 'metadata/management.html', {})


def database(request, database_name):
    return render(request, 'metadata/database.html', {
        'database': get_object_or_404(Database, name=database_name)
    })


def table(request, database_name, table_name):
    return render(request, 'metadata/table.html', {
        'table': get_object_or_404(Table, name=table_name, database__name=database_name)
    })
