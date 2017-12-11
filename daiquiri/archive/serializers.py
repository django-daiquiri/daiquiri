from rest_framework import serializers

from .models import ArchiveJob


class ArchiveSerializer(serializers.ModelSerializer):

    class Meta:
        model = ArchiveJob
        fields = (
            'files',
        )
