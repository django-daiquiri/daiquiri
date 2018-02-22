import logging

from django.shortcuts import render
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse

from .models import Meeting, Participant, Contribution
from .forms import ParticipantForm, ContributionForm
from .utils import send_registration_mails

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
            'participants': Participant.objects.filter(meeting=meeting, accepted=True)
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
            'contributions': Contribution.objects.filter(participant__meeting=meeting, accepted=True)
        })
    else:
        return render(request, 'meetings/contributions_closed.html', {})
