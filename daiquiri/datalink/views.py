from urllib.parse import urlencode, urlsplit, urlunsplit

from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse

from daiquiri.core.renderers.vosi import AvailabilityRenderer, CapabilitiesRenderer

from .adapter import DatalinkAdapter
from .constants import DATALINK_FIELDS
from .settings import DATALINK_CUSTOM_SEMANTICS
from .vo import get_availability, get_capabilities, get_link_list_name


def datalink(request, ID):
    adapter = DatalinkAdapter()
    context = adapter.get_context_data(request, ID=ID)
    context['datalinks'] = _visible_datalinks(context.get('datalinks', []))
    context['links_url'] = get_links_url('/', [ID])
    return render(request, 'datalink/datalink.html', context)


def datalink_view(request, endpoint_path='/'):
    identifiers = request.GET.getlist('ID')
    adapter = DatalinkAdapter(endpoint_path)
    field_names = [field['name'] for field in DATALINK_FIELDS]
    datalinks = [dict(zip(field_names, row)) for row in adapter.get_datalink_rows(identifiers)]

    context = {'datalinks': _visible_datalinks(datalinks)}
    context['links_url'] = get_links_url(endpoint_path, identifiers)
    if len(identifiers) == 1:
        context['ID'] = identifiers[0]
    return render(request, 'datalink/datalink.html', context)


def _visible_datalinks(datalinks):
    visible = []
    for datalink in datalinks:
        if datalink.get('service_def') or datalink.get('error_message'):
            continue

        access_url = datalink.get('access_url') or ''
        parts = urlsplit(access_url)
        path = parts.path.rstrip('/')
        path_prefix, separator, suffix = path.rpartition('/')
        if separator and suffix:
            datalink['access_url_prefix'] = urlunsplit(
                (parts.scheme, parts.netloc, f'{path_prefix}/', '', '')
            )
            suffix += '/' if parts.path.endswith('/') else ''
            datalink['access_url_suffix'] = urlunsplit(
                ('', '', suffix, parts.query, parts.fragment)
            )
        else:
            datalink['access_url_prefix'] = access_url
            datalink['access_url_suffix'] = ''
        visible.append(datalink)

    return visible


def get_links_url(endpoint_path, identifiers):
    url = reverse(f'datalink:{get_link_list_name(endpoint_path)}')
    query = urlencode([('ID', identifier) for identifier in identifiers])
    return f'{url}?{query}' if query else url


def datalink_semantics(request):
    context = { 'custom_semantics': DATALINK_CUSTOM_SEMANTICS }
    return render(request, 'datalink/datalink-semantics.html', context)

def availability(request):
    return HttpResponse(AvailabilityRenderer().render(get_availability()), content_type="application/xml")


def capabilities(request, endpoint_path='/'):
    return HttpResponse(
        CapabilitiesRenderer().render(get_capabilities(endpoint_path)),
        content_type="application/xml"
    )
