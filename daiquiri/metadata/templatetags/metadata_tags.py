from django import template
from django.utils.translation import ugettext_lazy as _

from daiquiri.core.constants import LICENSE_CHOICES, LICENSE_URLS

from ..models import Database

register = template.Library()


@register.inclusion_tag('metadata/tags/databases_menu.html', takes_context=True)
def databases_menu(context):

    databases = Database.objects.filter_by_metadata_access_level(context.request.user)

    context['databases'] = []
    for database in databases:
        context['databases'].append({
            'name': database.name,
            'tables': [table.name for table in database.tables.filter_by_metadata_access_level(context.request.user)]
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
