from django import forms
from django.utils.translation import ugettext as _

from .models import ContactMessage


class ContactForm(forms.ModelForm):

    class Meta:
        model = ContactMessage
        fields = ['author', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': _('Your name')}),
            'email': forms.TextInput(attrs={'placeholder': _('Your email address')}),
            'subject': forms.TextInput(attrs={'placeholder': _('Your subject')}),
            'message': forms.Textarea(attrs={'placeholder': _('Your message')}),
        }
        labels = {
            'name': _('Your name'),
            'email': _('Please enter your email address so our answer will reach you'),
            'message': _('Your message')
        }
