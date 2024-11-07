from django.http import HttpResponse
from django.shortcuts import render

from daiquiri.core.renderers.voresource import VoresourceRenderer
from daiquiri.core.renderers.vosi import AvailabilityRenderer, CapabilitiesRenderer, TablesetRenderer
from daiquiri.query.models import Example

from .vo import get_availability, get_capabilities, get_resource, get_tableset


def resource(request):
    return HttpResponse(VoresourceRenderer().render(get_resource()), content_type="application/xml")


def availability(request):
    return HttpResponse(AvailabilityRenderer().render(get_availability()), content_type="application/xml")


def capabilities(request):
    return HttpResponse(CapabilitiesRenderer().render(get_capabilities()), content_type="application/xml")


def tables(request):
    return HttpResponse(TablesetRenderer().render(get_tableset()), content_type="application/xml")


def examples(request):
    return render(request, 'tap/examples.html', {
        'examples': Example.objects.filter_by_access_level(request.user)
    })
