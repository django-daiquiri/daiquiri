from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _

from daiquiri.core.forms import HoneypotField
from daiquiri.core.utils import get_detail_fields, sanitize_str

from .models import Profile


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': _('First name')}),
            'last_name': forms.TextInput(attrs={'placeholder': _('Last name')}),
        }


class ProfileForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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

        return super().save(*args, **kwargs)


class SignupForm(ProfileForm):

    first_name = forms.CharField(max_length=30,
        label=_('First name'), widget=forms.TextInput(attrs={'placeholder': _('First name')}))
    last_name = forms.CharField(max_length=30,
        label=_('Last name'), widget=forms.TextInput(attrs={'placeholder': _('Last name')}))

    field_order = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # add a consent field, the label is added in the template
        if settings.AUTH_TERMS_OF_USE:
            tos_url = reverse('terms_of_use')
            self.fields['consent'] = forms.BooleanField()
            self.fields['consent'].label = mark_safe(f'I agree to the <a href="{tos_url}" data-bs-toggle="modal" '
                                                      'data-bs-target="#terms-of-use-modal">terms of use</a>.')
        # add honeypot field
        if settings.HONEYPOT_ENABLED is True:
            self.fields[sanitize_str(settings.HONEYPOT_FIELD_NAME)] = HoneypotField()

    def clean(self):
        if settings.AUTH_TERMS_OF_USE and not self.cleaned_data.get('consent'):
            raise ValidationError(_('You need to agree to the terms of use.'))

    def signup(self, request, user):
        # create an empty details dict
        user.profile.details = {}

        # store the form date for each detail key
        for detail_key in settings.AUTH_DETAIL_KEYS:
            user.profile.details[detail_key['key']] = self.cleaned_data[detail_key['key']]

        # store the consent field
        if settings.AUTH_TERMS_OF_USE:
            user.profile.consent = self.cleaned_data['consent']

        # save the profile model
        user.profile.save()
