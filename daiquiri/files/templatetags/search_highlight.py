from re import IGNORECASE, compile
from re import escape as rescape

from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='highlight')
def highlight(text, search):
    rgx = compile(rescape(search), IGNORECASE)
    return mark_safe(
        rgx.sub(
            lambda m: f'<b>{m.group()}</b>',
            text
        )
    )

@register.filter(name='underline')
def underline(text, search):
    rgx = compile(rescape(search), IGNORECASE)
    return mark_safe(
        rgx.sub(
            lambda m: f'<u>{m.group()}</u>',
            text
        )
    )
