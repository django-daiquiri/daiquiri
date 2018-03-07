from django import template
from django.utils.translation import ugettext_lazy as _

from daiquiri.core.constants import LICENSE_CHOICES, LICENSE_URLS

from ..models import Schema

register = template.Library()


@register.inclusion_tag('metadata/tags/schemas_menu.html', takes_context=True)
def schemas_menu(context):

    schemas = Schema.objects.filter_by_metadata_access_level(context.request.user)

    context['schemas'] = []
    for schema in schemas:
        context['schemas'].append({
            'name': schema.name,
            'tables': [table.name for table in schema.tables.filter_by_metadata_access_level(context.request.user)]
        })

    return context


@register.inclusion_tag('metadata/tags/doi_panel.html')
def doi_panel(doi, dataset=_('dataset')):
    return {
        'doi': doi,
        'dataset': dataset
    }


@register.inclusion_tag('metadata/tags/license_panel.html')
def license_panel(license):
    return {
        'license': license,
        'license_url': LICENSE_URLS[license],
        'license_label': dict(LICENSE_CHOICES)[license]
    }
