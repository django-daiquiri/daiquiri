from django import forms
from django.conf import settings
from django.core.exceptions import BadRequest
from django.forms.renderers import TemplatesSetting


class DaiquiriFormRenderer(TemplatesSetting):
    form_template_name = 'core/form/form.html'


class HoneypotInput(forms.TextInput):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs.update({
            'class': 'form-class', 'tabindex': '-1', 'autocomplete': 'off'
        })


class HoneypotField(forms.CharField):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', HoneypotInput())
        kwargs['required'] = False
        kwargs['label'] = '' if settings.HONEYPOT_FIELD_HIDDEN else settings.HONEYPOT_FIELD_NAME
        super().__init__(*args, **kwargs)

    def validate(self, value):
        return value == settings.HONEYPOT_FIELD_VALUE

    def clean(self, value):
        cleaned_value = super().clean(value)
        if self.validate(cleaned_value) is True:
            return cleaned_value
        else:
            raise BadRequest('invalid request')
