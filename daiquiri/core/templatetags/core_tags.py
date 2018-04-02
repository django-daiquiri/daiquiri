from markdown import markdown as markdown_function

from django import template
from django.conf import settings
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
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


@register.simple_tag()
@stringfilter
def vendor(vendor_key):
    vendor_config = settings.VENDOR[vendor_key]

    tags = []

    if 'js' in vendor_config:
        for file in vendor_config['js']:
            if settings.VENDOR_CDN:
                tag = '<script src="%(url)s/%(path)s" integrity="%(sri)s" crossorigin="anonymous"></script>' % {
                    'url': vendor_config['url'],
                    'path': file['path'],
                    'sri': file['sri'] if 'sri' in file else ''
                }
            else:
                tag = '<script src="%(static_url)s/%(vendor_key)s/%(path)s"></script>' % {
                    'static_url': settings.STATIC_URL.rstrip('/'),
                    'vendor_key': vendor_key,
                    'path': file['path']
                }

            tags.append(tag)

    if 'css' in vendor_config:
        for file in vendor_config['css']:
            if settings.VENDOR_CDN:
                tag = '<link rel="stylesheet" href="%(url)s/%(path)s" integrity="%(sri)s" crossorigin="anonymous" />' % {
                    'url': vendor_config['url'],
                    'path': file['path'],
                    'sri': file['sri'] if 'sri' in file else ''
                }
            else:
                tag = '<link rel="stylesheet" href="%(static_url)s/%(vendor_key)s/%(path)s" />' % {
                    'static_url': settings.STATIC_URL.rstrip('/'),
                    'vendor_key': vendor_key,
                    'path': file['path']
                }

            tags.append(tag)

    return mark_safe(''.join(tags))


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
