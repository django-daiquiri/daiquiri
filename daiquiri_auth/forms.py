from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from .models import DetailKey


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')


class ProfileForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)

        # add a field for first_name and last_name
        self.fields['first_name'] = forms.CharField()
        self.fields['first_name'].label = _('First name')
        self.fields['first_name'].required = True
        self.fields['last_name'] = forms.CharField()
        self.fields['last_name'].label = _('Last name')
        self.fields['last_name'].required = True

        # get the detail keys from the database
        detail_keys = DetailKey.objects.all()

        # add a field for each detail key
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


class SignupForm(ProfileForm):

    def signup(self, request, user):
        pass
