
from django import forms
from django.conf import settings
from django.utils.translation import gettext as _

from daiquiri.auth.forms import HoneypotField
from daiquiri.core.utils import sanitize_str

from .models import ContactMessage


class ContactForm(forms.ModelForm):

    use_required_attribute = False
    if settings.HONEYPOT_ENABLED is True:
        locals()[sanitize_str(settings.HONEYPOT_FIELD_NAME)] = HoneypotField()

    class Meta:
        model = ContactMessage
        fields = ['subject', 'message']
        widgets = {
            'subject': forms.TextInput(attrs={'placeholder': _('Subject')}),
            'message': forms.Textarea(attrs={'placeholder': _('Your message')}),
        }
        labels = {
            'subject': _('Subject'),
            'message': _('Your message')
        }
