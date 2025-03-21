from django.http import HttpResponse

from daiquiri.core.renderers.voresource import VoresourceRenderer
from daiquiri.core.renderers.vosi import AvailabilityRenderer, CapabilitiesRenderer

from .vo import get_availability, get_capabilities, get_resource


def resource(request):
    return HttpResponse(VoresourceRenderer().render(get_resource()), content_type="application/xml")


def availability(request):
    return HttpResponse(AvailabilityRenderer().render(get_availability()), content_type="application/xml")


def capabilities(request):
    return HttpResponse(CapabilitiesRenderer().render(get_capabilities()), content_type="application/xml")
