import os

from django import template
from django.template.defaultfilters import stringfilter
from django.urls import reverse
from django.utils.encoding import force_str
from django.utils.safestring import mark_safe

from markdown import markdown as markdown_function

from ..utils import get_script_alias

register = template.Library()


@register.simple_tag(takes_context=True)
def base_url(context):
    return get_script_alias(context.request) + '/'


@register.simple_tag(takes_context=True)
def absolute_url(context, name, *args):
    return context.request.build_absolute_uri(reverse(name, args=args))


@register.filter(name='next')
def next(value, arg):
    try:
        return value[int(arg)+1]
    except (ValueError, IndexError):
        return None


@register.filter(is_safe=True)
@stringfilter
def markdown(value):
    return mark_safe(markdown_function(force_str(value)))


@register.filter(is_safe=True)
@stringfilter
def semicolonbr(value):
    return mark_safe(value.replace(';', '<br />'))


@register.filter(is_safe=True)
@stringfilter
def to_safe_str(value):
    return mark_safe(str(value))


@register.filter()
def default_blank(value):
    return value if value else ''


@register.filter()
def default_blank_unit(value, unit):
    return str(value) + ' ' + unit if value else ''


@register.filter()
def basename(value):
    return os.path.basename(value)


@register.filter()
def startswith(text, starts):
    if isinstance(text, str):
        return text.startswith(starts)
    return False
