from django import template

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
