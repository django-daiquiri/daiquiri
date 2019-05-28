from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

from daiquiri.core.utils import get_script_alias
from daiquiri.wordpress.utils import get_menu

register = template.Library()


@register.simple_tag(takes_context=True)
def wordpress_url(context, path=None):
    url = get_script_alias(context.request) + settings.WORDPRESS_URL

    if path:
        url += path

    return url


@register.simple_tag(takes_context=True)
def wordpress_admin_url(context):
    return get_script_alias(context.request) + settings.WORDPRESS_URL + 'wp-admin/'


@register.simple_tag(takes_context=True)
def wordpress_menu(context, menu_name):
    return mark_safe(get_menu(context.request, menu_name))
