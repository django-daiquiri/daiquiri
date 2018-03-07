from django import forms
from django.conf import settings
from django.utils.timezone import now
from django.utils.translation import ugettext as _

from daiquiri.core.utils import get_detail_fields

from .models import Participant, Contribution


class ParticipantForm(forms.ModelForm):

    class Meta:
        model = Participant
        fields = ('first_name', 'last_name', 'email')
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': _('First name')}),
            'last_name': forms.TextInput(attrs={'placeholder': _('Last name')}),
            'email': forms.TextInput(attrs={'placeholder': _('Email')})
        }

    def __init__(self, *args, **kwargs):
        self.meeting = kwargs.pop('meeting')
        super(ParticipantForm, self).__init__(*args, **kwargs)

        for key, field in get_detail_fields(settings.MEETINGS_PARTICIPANT_DETAIL_KEYS):
            self.fields[key] = field

    def save(self, *args, **kwargs):
        # set the meeting and the current time
        self.instance.meeting = self.meeting
        self.instance.registered = now()

        # create an empty details dict if it does not exist
        if not self.instance.details:
            self.instance.details = {}

        # store the form date for each detail key
        for detail_key in settings.MEETINGS_PARTICIPANT_DETAIL_KEYS:
            self.instance.details[detail_key['key']] = self.cleaned_data[detail_key['key']]

        return super(ParticipantForm, self).save(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data['email']

        try:
            self.meeting.participants.get(email=email)
            self.add_error('email', _('You have already registred with this email address.'))
        except Participant.DoesNotExist:
            pass

        return email


class ContributionForm(forms.ModelForm):

    contribution_type = forms.ChoiceField(
        choices=settings.MEETINGS_CONTRIBUTION_TYPES,
        widget=forms.RadioSelect,
        help_text=None,
        required=None
    )
    title = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': _('Title')}),
        required=None
    )
    abstract = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': _('Abstract')}),
        required=None,
        max_length=settings.MEETINGS_ABSTRACT_MAX_LENGTH,
        help_text=_('The abstract needs to be shorter than %s characters.') % settings.MEETINGS_ABSTRACT_MAX_LENGTH
    )

    class Meta:
        model = Contribution
        fields = ('contribution_type', 'title', 'abstract')

    def clean(self):
        cleaned_data = super(ContributionForm, self).clean()

        # if the contribution_type is set, title and abstract need to be provided
        if 'contribution_type' in cleaned_data and cleaned_data['contribution_type']:
            if not cleaned_data['title']:
                self.add_error('title', _('This field is required.'))

            if not cleaned_data['abstract']:
                self.add_error('abstract', _('This field is required.'))
        else:
            if cleaned_data['title'] or cleaned_data['abstract']:
                self.add_error('contribution_type', _('This field is required.'))
