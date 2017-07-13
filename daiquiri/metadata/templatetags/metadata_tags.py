from django import template

from ..models import Database

register = template.Library()


@register.inclusion_tag('metadata/tags/databases_menu.html', takes_context=True)
def databases_menu(context):
    return {
        'databases': Database.objects.filter_by_metadata_access_level(context.request.user)
    }
