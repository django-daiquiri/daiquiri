from django.http import HttpResponse
from django.shortcuts import render

from daiquiri.core.renderers.vosi import AvailabilityRenderer, CapabilitiesRenderer

from .adapter import DatalinkAdapter
from .settings import DATALINK_CUSTOM_SEMANTICS
from .vo import get_availability, get_capabilities


def datalink(request, ID):
    adapter = DatalinkAdapter()
    context = adapter.get_context_data(request, ID=ID)
    context['custom_semantics'] = DATALINK_CUSTOM_SEMANTICS
    return render(request, 'datalink/datalink.html', context)

def datalink_semantics(request):
    context = { 'custom_semantics': DATALINK_CUSTOM_SEMANTICS }
    return render(request, 'datalink/datalink-semantics.html', context)

def availability(request):
    return HttpResponse(AvailabilityRenderer().render(get_availability()), content_type="application/xml")


def capabilities(request):
    return HttpResponse(CapabilitiesRenderer().render(get_capabilities()), content_type="application/xml")
