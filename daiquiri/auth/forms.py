from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from daiquiri.core.utils import get_detail_fields

from .models import Profile


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': _('First name')}),
            'last_name': forms.TextInput(attrs={'placeholder': _('Last name')})
        }


class ProfileForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ()

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)

        for key, field in get_detail_fields(settings.AUTH_DETAIL_KEYS):
            if self.instance.details and key in self.instance.details:
                field.initial = self.instance.details[key]

            self.fields[key] = field

    def save(self, *args, **kwargs):
        # create an empty details dict if it does not exist
        if not self.instance.details:
            self.instance.details = {}

        # store the form date for each detail key
        for detail_key in settings.AUTH_DETAIL_KEYS:
            self.instance.details[detail_key['key']] = self.cleaned_data[detail_key['key']]

        return super(ProfileForm, self).save(*args, **kwargs)


class SignupForm(ProfileForm):

    first_name = forms.CharField(max_length=30, label=_('First name'), widget=forms.TextInput(attrs={'placeholder': _('First name')}))
    last_name = forms.CharField(max_length=30, label=_('Last name'), widget=forms.TextInput(attrs={'placeholder': _('Last name')}))

    def signup(self, request, user):
        # create an empty details dict
        user.profile.details = {}

        # store the form date for each detail key
        for detail_key in settings.AUTH_DETAIL_KEYS:
            user.profile.details[detail_key['key']] = self.cleaned_data[detail_key['key']]

        # save the profile model
        user.profile.save()
