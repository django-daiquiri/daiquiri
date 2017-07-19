from django.shortcuts import render

from daiquiri.query.models import Example

from .models import Schema


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
