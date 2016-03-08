from django import forms
from django.contrib.auth.models import User


class LoginForm(forms.Form):
    username = forms.CharField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class ProfileForm(forms.Form):
    def __init__(self, *args, **kwargs):
        profile = kwargs.pop('profile')
        detail_keys = kwargs.pop('detail_keys')

        super(ProfileForm, self).__init__(*args, **kwargs)

        # add fields and init values for the Profile model
        for detail_key in detail_keys:
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
            self.fields[detail_key.key] = field

            # add an initial value, if one is found in the user details
            if profile.details and detail_key.key in profile.details:
                self.fields[detail_key.key].initial = profile.details[detail_key.key]
