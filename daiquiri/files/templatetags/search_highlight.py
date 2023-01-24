from django import template
from re import IGNORECASE, compile, escape as rescape
from django.utils.safestring import mark_safe


register = template.Library()

@register.filter(name='highlight')
def highlight(text, search):
    rgx = compile(rescape(search), IGNORECASE)
    return mark_safe(
        rgx.sub(
            lambda m: '<b>{}</b>'.format(m.group()),
            text
        )
    )

@register.filter(name='underline')
def underline(text, search):
    rgx = compile(rescape(search), IGNORECASE)
    return mark_safe(
        rgx.sub(
            lambda m: '<u>{}</u>'.format(m.group()),
            text
        )
    )
