from rest_framework import serializers

from .models import Proposal


class ProposalSerializer(serializers.ModelSerializer):

    class Meta:
        model = Proposal
        fields = '__all__'
