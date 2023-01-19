from django import forms
from django.utils.translation import gettext as _

from .models import ContactMessage


class ContactForm(forms.ModelForm):

    use_required_attribute = False

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
