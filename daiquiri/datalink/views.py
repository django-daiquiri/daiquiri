from django.http import HttpResponse

from daiquiri.core.renderers.vosi import AvailabilityRenderer, CapabilitiesRenderer

from .vo import get_availability, get_capabilities


def availability(request):
    return HttpResponse(AvailabilityRenderer().render(get_availability()), content_type="application/xml")


def capabilities(request):
    return HttpResponse(CapabilitiesRenderer().render(get_capabilities()), content_type="application/xml")
