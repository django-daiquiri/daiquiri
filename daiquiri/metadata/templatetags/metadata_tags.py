from django import template
from django.conf import settings
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from daiquiri.core.utils import get_doi_url

from ..models import Schema

register = template.Library()


@register.inclusion_tag('metadata/tags/schemas_menu.html', takes_context=True)
def schemas_menu(context, tables=True):

    schemas = Schema.objects.filter_by_metadata_access_level(context.request.user)

    context['schemas'] = []
    for schema in schemas:
        context['schemas'].append({
            'name': schema.name,
            'label': schema.title or schema.name,
            'tables': [{
                'name': table.name,
                'label': f'{schema.name}.{table.name}'
                } for table in schema.tables.filter_by_metadata_access_level(context.request.user)
            ] if tables else []
        })

    return context


@register.inclusion_tag('metadata/tags/access_panel.html')
def access_panel(doi, dataset=None):
    return {
        'dataset': dataset or _('dataset')
    }


@register.simple_tag()
def doi_link(doi):
    url = get_doi_url(doi)
    return format_html('<a class="break" href="{}">{}</a>', url, url)


@register.inclusion_tag('metadata/tags/doi_panel.html')
def doi_panel(doi, dataset=None):
    return {
        'doi_url': get_doi_url(doi),
        'dataset': dataset or _('dataset')
    }


@register.inclusion_tag('metadata/tags/license_panel.html')
def license_panel(license, dataset=None):
    return {
        'license': license,
        'license_url': settings.LICENSE_URLS[license],
        'license_label': dict(settings.LICENSE_CHOICES)[license],
        'dataset': dataset or _('dataset')
    }
