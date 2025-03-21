from django import forms
from django.conf import settings
from django.utils.translation import gettext as _

from daiquiri.core.forms import HoneypotField
from daiquiri.core.utils import sanitize_str

from .models import ContactMessage


class ContactForm(forms.ModelForm):

    use_required_attribute = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # add honeypot field
        if settings.HONEYPOT_ENABLED is True:
            self.fields[sanitize_str(settings.HONEYPOT_FIELD_NAME)] = HoneypotField()

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
