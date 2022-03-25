from django.http import HttpResponse
from django.shortcuts import render

from daiquiri.core.renderers.vosi import AvailabilityRenderer, CapabilitiesRenderer

from .models import Datalink
from .vo import get_availability, get_capabilities


def datalink(request, ID):
    datalinks = Datalink.objects.filter(ID=ID)

    return render(request, 'datalink/datalink.html', {
        'ID': ID,
        'datalinks': datalinks
    })


def availability(request):
    return HttpResponse(AvailabilityRenderer().render(get_availability()), content_type="application/xml")


def capabilities(request):
    return HttpResponse(CapabilitiesRenderer().render(get_capabilities()), content_type="application/xml")
