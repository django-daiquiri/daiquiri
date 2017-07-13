from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseBadRequest
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from rest_framework.exceptions import ValidationError

from daiquiri.core.http import HttpResponseSeeOther
from daiquiri.query.models import QueryJob, Example
from daiquiri.query.utils import get_default_table_name
from daiquiri.query.exceptions import (
    ADQLSyntaxError,
    MySQLSyntaxError,
    PermissionError,
    TableError,
    ConnectionError
)


from .models import Schema, Table, Column


@csrf_exempt
def sync(request):
    if request.method == 'POST':

        query_language = request.POST.get('LANG').lower()
        query = request.POST.get('QUERY')

        try:
            job_id = QueryJob.objects.submit(
                query_language,
                query,
                None,
                get_default_table_name(),
                request.user,
                sync=True
            )
        except (ADQLSyntaxError, MySQLSyntaxError,PermissionError, ConnectionError, TableError) as e:
            return HttpResponseBadRequest(e.message)

        return HttpResponseSeeOther(reverse('query:job-download', kwargs={
            'pk': str(job_id),
            'format_key': 'votable'
        }))
    else:
        return HttpResponseNotAllowed(['POST'])

@csrf_exempt
def async(request):
    if request.method == 'POST':
        return HttpResponse()
    else:
        return HttpResponseNotAllowed(['POST'])

def capabilities(request):
    return render(request, 'tap/capabilities.xml', content_type='application/xml')

def tables(request):
    return render(request, 'tap/tables.xml', {
        'schemas': Schema.objects.using('tap').all()
    }, content_type='application/xml')

def examples(request):
    return render(request, 'tap/examples.html', {
        'examples': Example.objects.all()
    })
