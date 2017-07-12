from django import template

from ..models import Database

register = template.Library()


@register.inclusion_tag('metadata/tags/databases_menu.html', takes_context=True)
def databases_menu(context):
    databases = Database.permissions.all(context.request.user)
    return {'databases': databases}
