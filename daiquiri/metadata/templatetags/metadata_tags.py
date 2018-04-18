from django import template
from django.utils.translation import ugettext_lazy as _

from daiquiri.core.constants import LICENSE_CHOICES, LICENSE_URLS
from daiquiri.core.utils import get_doi_url

from ..models import Schema

register = template.Library()


@register.inclusion_tag('metadata/tags/schemas_menu.html', takes_context=True)
def schemas_menu(context):

    schemas = Schema.objects.filter_by_metadata_access_level(context.request.user)

    context['schemas'] = []
    for schema in schemas:
        context['schemas'].append({
            'name': schema.name,
            'label': schema.title or schema.name,
            'tables': [{
                'name': table.name,
                'label': '%s.%s' % (schema.name, table.name)
                } for table in schema.tables.filter_by_metadata_access_level(context.request.user)
            ]
        })

    return context


@register.inclusion_tag('metadata/tags/access_panel.html')
def access_panel(doi, dataset=_('dataset')):
    return {
        'dataset': dataset
    }


@register.inclusion_tag('metadata/tags/doi_panel.html')
def doi_panel(doi, dataset=_('dataset')):
    return {
        'doi_url': get_doi_url(doi),
        'dataset': dataset
    }


@register.inclusion_tag('metadata/tags/license_panel.html')
def license_panel(license):
    return {
        'license': license,
        'license_url': LICENSE_URLS[license],
        'license_label': dict(LICENSE_CHOICES)[license]
    }
