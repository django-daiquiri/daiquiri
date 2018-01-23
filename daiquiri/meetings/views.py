from django.shortcuts import render
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse

from .models import Meeting, Participant, Contribution
from .forms import ParticipantForm, ContributionForm


def registration(request, slug):
    print(slug)
    try:
        meeting = Meeting.objects.filter(registration_open=True).get(slug=slug)
    except Meeting.DoesNotExist:
        raise Http404

    participant_form = ParticipantForm(request.POST or None, meeting=meeting)
    contribution_form = ContributionForm(request.POST or None)

    if request.method == 'POST':
        if participant_form.is_valid() and contribution_form.is_valid():
            participant = participant_form.save()

            contribution = contribution_form.save(commit=False)
            contribution.participant = participant
            contribution.save()

            return HttpResponseRedirect(reverse('meetings:registration_done', kwargs={'slug': slug}))

    return render(request, 'meetings/registration.html', {
        'meeting': meeting,
        'participant_form': participant_form,
        'contribution_form': contribution_form
    })


def registration_done(request, slug):
    try:
        meeting = Meeting.objects.filter(registration_open=True).get(slug=slug)
    except Meeting.DoesNotExist:
        raise Http404

    return render(request, 'meetings/registration_done.html', {
        'meeting': meeting,
    })


def participants(request, slug):

    try:
        meeting = Meeting.objects.filter(participants_open=True).get(slug=slug)
    except Meeting.DoesNotExist:
        raise Http404

    return render(request, 'meetings/participants.html', {
        'meeting': meeting,
        'participants': Participant.objects.filter(meeting=meeting, accepted=True)
    })


def contributions(request, slug):
    try:
        meeting = Meeting.objects.filter(contributions_open=True).get(slug=slug)
    except Meeting.DoesNotExist:
        raise Http404

    return render(request, 'meetings/contributions.html', {
        'meeting': meeting,
        'contributions': Contribution.objects.filter(participant__meeting=meeting, accepted=True)
    })
