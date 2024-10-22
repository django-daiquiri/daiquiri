from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import BadRequest, ValidationError
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from django.urls import reverse

from daiquiri.core.utils import get_detail_fields, sanitize_str

from .models import Profile


class HoneypotField(forms.CharField):
    hpstyle = 'border: 1px dashed'
    hplabel = settings.HONEYPOT_FIELD_NAME
    if settings.HONEYPOT_FIELD_HIDDEN is True:
        hpstyle = 'opacity: 0; position: absolute; top: 0; left: 0; height: 0; width: 0; z-index: -1;'
        hplabel = ''
    default_widget = forms.TextInput(
        {'style': hpstyle, 'tabindex': '-1', 'autocomplete': 'off'}
    )

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', HoneypotField.default_widget)
        kwargs['required'] = False
        kwargs['label'] = self.hplabel
        super().__init__(*args, **kwargs)

    def validate(self, value):
        return value == settings.HONEYPOT_FIELD_VALUE

    def clean(self, value):
        cleaned_value = super().clean(value)
        if self.validate(cleaned_value) is True:
            return cleaned_value
        else:
            raise BadRequest('invalid request')

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

    first_name = forms.CharField(max_length=30,
        label=_('First name'), widget=forms.TextInput(attrs={'placeholder': _('First name')}))
    last_name = forms.CharField(max_length=30,
        label=_('Last name'), widget=forms.TextInput(attrs={'placeholder': _('Last name')}))
    if settings.HONEYPOT_ENABLED is True:
        locals()[sanitize_str(settings.HONEYPOT_FIELD_NAME)] = HoneypotField()

    field_order = ['username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)

        # add a consent field, the label is added in the template
        if settings.AUTH_TERMS_OF_USE:
            tos_url = reverse('terms_of_use')
            self.fields['consent'] = forms.BooleanField()
            self.fields['consent'].label = mark_safe(f'I agree to the <a href="{tos_url}" data-bs-toggle="modal" '
                                                      'data-bs-target="#terms-of-use-modal">terms of use</a>.')

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
