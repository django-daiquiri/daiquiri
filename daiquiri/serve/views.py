from django.http import Http404
from django.shortcuts import redirect, render

from daiquiri.metadata.utils import get_user_columns, get_table_metadata

from .utils import get_resolver


def table(request, schema_name, table_name):

    if get_user_columns(request.user, schema_name, table_name):
        table = get_table_metadata(request.user, schema_name, table_name)

        context = {}
        if table is not None:
            context['table_title'] = table.title
            context['table_name'] = table.name
            context['schema_name'] = table.schema.name
            context['table_description'] = table.long_description

        return render(request, 'serve/table.html', context)

    # if nothing worked, return 404
    raise Http404

def reference(request, key, value):

    resolver = get_resolver()
    if resolver is None:
        raise Http404()

    url = resolver.resolve(request, key, value)
    if url is None:
        raise Http404()

    return redirect(url)
