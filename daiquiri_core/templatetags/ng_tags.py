from django import template
from django.template.loader import render_to_string

register = template.Library()


@register.simple_tag()
def ng_form_field(field_type, label, field, ng_model):
    print field_type

    if field_type == 'text':
        return render_to_string('core/ng_form_field_text.html', {
            'label': label,
            'field': field,
            'ng_model': ng_model
        })
    elif field_type == 'checkbox':
        return render_to_string('core/ng_form_field_checkbox.html', {
            'label': label,
            'field': field,
            'ng_model': ng_model
        })
    else:
        raise Exception('Field type "%s" not found' % field_type)
