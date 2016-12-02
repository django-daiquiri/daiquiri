from django import forms
# from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from .models import ContactMessage





class ContactForm(forms.ModelForm):

    class Meta:
        model = ContactMessage
        fields = ('first_name', 'last_name', 'email', 'category', 'subject', 'message')

    #contact_name = forms.CharField(max_length=30, label=_('Your first name'),
    #                               widget=forms.TextInput(attrs={'placeholder': _('Your first name')}))
    #contact_name = forms.CharField(max_length=30, label=_('Your surname'),
    #                               widget=forms.TextInput(attrs={'placeholder': _('Your surname')}))
    #contact_email = forms.CharField(max_length=30, label=_('Your email'),
    #                            widget=forms.TextInput(attrs={'placeholder': _('Your email')}))
    #contact_subject = forms.CharField(max_length=30, label=_('Subject'),
    #                              widget=forms.TextInput(attrs={'placeholder': _('Subject')}))
    contact_message = forms.CharField(max_length=450, label=_('Your message'),
                                  widget=forms.Textarea(attrs={'placeholder': _('Your message')}))


    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)



