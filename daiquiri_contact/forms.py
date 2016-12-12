from django import forms
# from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from .models import ContactMessage





class ContactForm(forms.ModelForm):

    class Meta:
        model = ContactMessage
        fields = ()

    name = forms.CharField(max_length=30, label=_('Your name'),
                               widget=forms.TextInput(attrs={'placeholder': _('Your name')}))
    email = forms.CharField(max_length=30, label=_('Your email'),
                                widget=forms.TextInput(attrs={'placeholder': _('Your email')}))
    subject = forms.CharField(max_length=30, label=_('Subject'),
                                  widget=forms.TextInput(attrs={'placeholder': _('Subject')}))
    # category = forms.ChoiceInput(choices=ContactMessage.category)
    message = forms.CharField(max_length=450, label=_('Your message'),
                                  widget=forms.Textarea(attrs={'placeholder': _('Your message')}))


    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)


    def save(self, *args, **kwargs):
        # create an empty details dict if it does not exist
        if not self.instance.details:
            self.instance.details = {}

        # store the form date for each detail key
        for detail_key in self.detail_keys:
            self.instance.details[detail_key.key] = self.cleaned_data[detail_key.key]

        return super(ContactForm, self).save(*args, **kwargs)