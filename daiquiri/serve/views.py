from django.shortcuts import render
from django.http import Http404
from django.shortcuts import redirect

from daiquiri.metadata.utils import get_user_columns

from .utils import get_resolver


def table(request, schema_name, table_name):

    if get_user_columns(request.user, schema_name, table_name):
        return render(request, 'serve/table.html', {
            'schema': schema_name,
            'table': table_name
        })

    # if nothing worked, return 404
    raise Http404


def reference(request, key, value):

    resolver = get_resolver()
    if resolver is None:
        raise Http404()

    url = resolver.resolve(key, value)
    if url is None:
        raise Http404()

    return redirect(url)
