import json
import logging

from django.conf import settings
from django.shortcuts import render
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from django.views.generic import View, TemplateView
from django.utils.translation import ugettext_lazy as _

from daiquiri.core.views import ModelPermissionMixin
from daiquiri.core.utils import get_model_field_meta, render_to_csv, render_to_xlsx

from .models import Meeting, Participant, Contribution
from .forms import ParticipantForm, ContributionForm
from .utils import send_registration_mails
from .filters import ParticipantFilterBackend

logger = logging.getLogger(__name__)


def registration(request, slug):
    try:
        meeting = Meeting.objects.get(slug=slug)
    except Meeting.DoesNotExist:
        raise Http404

    if meeting.registration_open:
        participant_form = ParticipantForm(request.POST or None, meeting=meeting)
        contribution_form = ContributionForm(request.POST or None)

        if request.method == 'POST':
            if participant_form.is_valid() and contribution_form.is_valid():
                participant = participant_form.save()

                logger.info('participant \'%s\' registered.' % (participant.full_name, ))

                if contribution_form.cleaned_data['contribution_type']:
                    contribution = contribution_form.save(commit=False)
                    contribution.participant = participant
                    contribution.save()

                    send_registration_mails(request, meeting, participant, contribution)
                else:
                    send_registration_mails(request, meeting, participant)

                return HttpResponseRedirect(reverse('meetings:registration_done', kwargs={
                    'slug': slug
                }))

        return render(request, 'meetings/registration.html', {
            'meeting': meeting,
            'participant_form': participant_form,
            'contribution_form': contribution_form
        })
    else:
        return render(request, 'meetings/registration_closed.html', {})


def registration_done(request, slug):
    try:
        meeting = Meeting.objects.get(slug=slug)
    except Meeting.DoesNotExist:
        raise Http404

    if meeting.registration_open:
        return render(request, 'meetings/registration_done.html', {
            'meeting': meeting,
        })
    else:
        return render(request, 'meetings/registration_closed.html', {})


def participants(request, slug):
    try:
        meeting = Meeting.objects.get(slug=slug)
    except Meeting.DoesNotExist:
        raise Http404

    if meeting.participants_open:
        return render(request, 'meetings/participants.html', {
            'meeting': meeting,
            'participants': Participant.objects.filter(meeting=meeting),
            'contributions': Contribution.objects.filter(participant__meeting=meeting)
        })
    else:
        return render(request, 'meetings/participants_closed.html', {})


def contributions(request, slug):
    try:
        meeting = Meeting.objects.get(slug=slug)
    except Meeting.DoesNotExist:
        raise Http404

    if meeting.contributions_open:
        return render(request, 'meetings/contributions.html', {
            'meeting': meeting,
            'participants': Participant.objects.filter(meeting=meeting),
            'contributions': Contribution.objects.filter(participant__meeting=meeting)
        })
    else:
        return render(request, 'meetings/contributions_closed.html', {})


class ManagementView(ModelPermissionMixin, TemplateView):

    template_name = 'meetings/management.html'
    permission_required = (
        'daiquiri_meetings.view_meeting',
        'daiquiri_meetings.view_participant',
        'daiquiri_meetings.view_contribution'
    )

    def get_context_data(self, **kwargs):
        context = super(ManagementView, self).get_context_data(**kwargs)

        try:
            meeting = Meeting.objects.get(slug=kwargs['slug'])
        except Meeting.DoesNotExist:
            raise Http404

        # get urls to the admin interface to be used with angular
        meeting_admin_url = reverse('admin:daiquiri_meetings_meeting_change', args=[meeting.id])
        participant_admin_url = reverse('admin:daiquiri_meetings_participant_change', args=['row.id']).replace('row.id', '{$ row.id $}')
        contribution_admin_url = reverse('admin:daiquiri_meetings_contribution_change', args=['row.id']).replace('row.id', '{$ row.id $}')

        detail_keys = settings.MEETINGS_PARTICIPANT_DETAIL_KEYS
        for detail_key in detail_keys:
            detail_key['options_json'] = json.dumps(detail_key.get('options', {}))
            detail_key['model'] = 'service.values.details.%s' % detail_key['key']
            detail_key['errors'] = 'service.errors.%s' % detail_key['key']

        context.update({
            'meeting_id': meeting.id,
            'meeting_slug': meeting.slug,
            'detail_keys': detail_keys,
            'meeting_admin_url': meeting_admin_url,
            'participant_admin_url': participant_admin_url,
            'contribution_admin_url': contribution_admin_url,
            'statuses': ['all'] + [label for _, label in Participant.STATUS_CHOICES],
            'meta': {
                'Meeting': get_model_field_meta(Meeting),
                'Participant': get_model_field_meta(Participant),
                'Contribution': get_model_field_meta(Contribution)
            }
        })
        return context


class ExportView(ModelPermissionMixin, View):

    permission_required = (
        'daiquiri_meetings.view_meeting',
        'daiquiri_meetings.view_participant',
        'daiquiri_meetings.view_contribution'
    )

    def get_meeting(self, slug):
        try:
            return Meeting.objects.get(slug=slug)
        except Meeting.DoesNotExist:
            raise Http404


class ParticipantExportView(ExportView):

    def get_columns(self):
        detail_keys = settings.MEETINGS_PARTICIPANT_DETAIL_KEYS

        return [
            _('First name'),
            _('Last name'),
            _('Email'),
            _('Registered'),
            _('Status')
        ] + [detail_key['label'] for detail_key in detail_keys] + [
            _('Contribution title'),
            _('Contribution abstract'),
            _('Contribution type'),
            _('Contribution accepted')
        ]

    def get_rows(self, participants):
        detail_keys = settings.MEETINGS_PARTICIPANT_DETAIL_KEYS

        for participant in participants:
            contribution = participant.contributions.first()

            row = [
                participant.first_name,
                participant.last_name,
                participant.email,
                participant.registered,
                participant.get_status_display()
            ]

            if participant.details:
                for detail_key in detail_keys:
                    if participant.details and detail_key['key'] in participant.details:
                        row.append(participant.details[detail_key['key']])
                    else:
                        row.append('')

            if contribution:
                row += [
                    contribution.title,
                    contribution.abstract,
                    contribution.get_contribution_type_display(),
                    contribution.accepted
                ]

            yield row

    def get(self, request, slug, format):
        meeting = self.get_meeting(slug)
        participants = meeting.participants.all()

        if format == 'csv':
            return render_to_csv(request, meeting.title, self.get_columns(), self.get_rows(participants))
        elif format == 'xlsx':
            return render_to_xlsx(request, meeting.title, self.get_columns(), self.get_rows(participants))
        else:
            raise Http404


class AbstractExportView(ExportView):

    def get(self, request, slug):

        meeting = self.get_meeting(slug)

        queryset = meeting.participants.all()
        participants = ParticipantFilterBackend().filter_queryset(request, queryset, self)

        return render(request, 'meetings/export_abstracts.html', {
            'meeting': meeting,
            'participants': participants
        })


class EmailExportView(ExportView):

    def get(self, request, slug):

        meeting = self.get_meeting(slug)

        queryset = meeting.participants.all()
        participants = ParticipantFilterBackend().filter_queryset(request, queryset, self)

        return render(request, 'meetings/export_emails.html', {
            'meeting': meeting,
            'participants': participants
        }, content_type='text/plain; charset=utf-8')
