from django import forms
from django.utils.translation import ugettext as _

from .models import ContactMessage


class ContactForm(forms.ModelForm):

    use_required_attribute = False

    class Meta:
        model = ContactMessage
        fields = ['author', 'email', 'subject', 'message']
        widgets = {
            'author': forms.TextInput(attrs={'placeholder': _('Your name')}),
            'email': forms.TextInput(attrs={'placeholder': _('Your email address')}),
            'subject': forms.TextInput(attrs={'placeholder': _('Subject')}),
            'message': forms.Textarea(attrs={'placeholder': _('Your message')}),
        }
        labels = {
            'author': _('Your name'),
            'email': _('Please enter your email address so our answer will reach you'),
            'message': _('Your message')
        }
