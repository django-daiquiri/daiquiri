import os

from django import template
from django.conf import settings
from django.core.files import File
from django.utils.safestring import mark_safe

from daiquiri.core.utils import get_script_alias

register = template.Library()


@register.simple_tag(takes_context=True)
def wordpress_url(context):
    return get_script_alias(context.request) + settings.WORDPRESS_URL


@register.simple_tag(takes_context=True)
def wordpress_admin_url(context):
    return get_script_alias(context.request) + settings.WORDPRESS_URL + 'wp-admin/'


@register.simple_tag()
def wordpress_menu(menu_name):

    with open(os.path.join(settings.WORDPRESS_PATH, 'wp-content', 'menus', menu_name + '.html')) as f:
        menu_file = File(f)
        menu_string = menu_file.read()

    return mark_safe(menu_string)
