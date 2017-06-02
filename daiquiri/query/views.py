from django.conf import settings
from django.contrib.auth.decorators import login_required

from django.shortcuts import render


@login_required()
def query(request):
    return render(request, 'query/query.html', {
        'query_settings': settings.QUERY
    })


def examples(request):
    return render(request, 'query/examples.html', {})
