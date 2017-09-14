from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

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

        # add a field for each detail key
        for detail_key in settings.AUTH_DETAIL_KEYS:

            choices = [(option['id'], option['label']) for option in detail_key['options']]

            if detail_key['data_type'] == 'text':
                field = forms.CharField(widget=forms.TextInput(attrs={'placeholder': detail_key['label']}))
            elif detail_key['data_type'] == 'textarea':
                field = forms.CharField(widget=forms.Textarea(attrs={'placeholder': detail_key['label']}))
            elif detail_key['data_type'] == 'select':
                field = forms.ChoiceField(choices=choices)
            elif detail_key['data_type'] == 'radio':
                field = forms.ChoiceField(choices=choices, widget=forms.RadioSelect)
            elif detail_key['data_type'] == 'multiselect':
                field = forms.MultipleChoiceField(choices=choices)
            elif detail_key['data_type'] == 'checkbox':
                field = forms.MultipleChoiceField(choices=choices, widget=forms.CheckboxSelectMultiple)
            else:
                raise Exception('Unknown detail key data type.')

            if 'label' in detail_key:
                field.label = detail_key['label']

            if 'required' in detail_key:
                field.required = detail_key['required']

            if 'help_text' in detail_key:
                field.help_text = detail_key['help_text']

            if self.instance.details and detail_key['key'] in self.instance.details:
                field.initial = self.instance.details[detail_key['key']]

            self.fields[detail_key['key']] = field

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
