from django import forms
from django.contrib.auth.models import User

from .models import DetailKey, Profile


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class ProfileForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = ()

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)

        # get the detail keys from the database
        self.detail_keys = DetailKey.objects.all()

        # add a field for each detail key
        for detail_key in self.detail_keys:
            if detail_key.data_type == 'text':
                field = forms.CharField()
            elif detail_key.data_type == 'textarea':
                field = forms.CharField(widget=forms.Textarea)
            elif detail_key.data_type == 'select':
                field = forms.ChoiceField(choices=detail_key.options)
            elif detail_key.data_type == 'radio':
                field = forms.ChoiceField(choices=detail_key.options, widget=forms.RadioSelect)
            elif detail_key.data_type == 'multiselect':
                field = forms.MultipleChoiceField(choices=detail_key.options)
            elif detail_key.data_type == 'checkbox':
                field = forms.MultipleChoiceField(choices=detail_key.options, widget=forms.CheckboxSelectMultiple)
            else:
                raise Exception('Unknown detail key data type.')

            field.label = detail_key.label
            field.required = detail_key.required
            field.help_text = detail_key.help_text

            if self.instance.details and detail_key.key in self.instance.details:
                field.initial = self.instance.details[detail_key.key]

            self.fields[detail_key.key] = field

    def save(self, *args, **kwargs):
        # create an empty details dict if it does not exist
        if not self.instance.details:
            self.instance.details = {}

        # store the form date for each detail key
        for detail_key in self.detail_keys:
            self.instance.details[detail_key.key] = self.cleaned_data[detail_key.key]

        return super(ProfileForm, self).save(*args, **kwargs)


class SignupForm(ProfileForm):

    def signup(self, request, user):
        pass
