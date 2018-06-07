from rest_framework import serializers

from daiquiri.core.serializers import JSONField

from .models import Meeting, Participant, Contribution


class MeetingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Meeting
        fields = (
            'id',
            'title',
            'registration_message',
            'registration_done_message',
            'participants_message',
            'contributions_message',
            'registration_open',
            'participants_open',
            'contributions_open'
        )


class ContributionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Contribution
        fields = (
            'id',
            'participant',
            'title',
            'abstract',
            'contribution_type',
            'accepted'
        )


class ParticipantSerializer(serializers.ModelSerializer):

    details = JSONField(allow_null=True)
    contributions = ContributionSerializer(many=True, read_only=True)

    class Meta:
        model = Participant
        fields = (
            'id',
            'first_name',
            'last_name',
            'email',
            'details',
            'registered',
            'status',
            'contributions'
        )
