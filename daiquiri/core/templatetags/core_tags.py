import os

from markdown import markdown as markdown_function

from django import template
from django.urls import reverse
from django.template.defaultfilters import stringfilter
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe

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
    except:
        return None


@register.filter(is_safe=True)
@stringfilter
def markdown(value):
    return mark_safe(markdown_function(force_text(value)))


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
