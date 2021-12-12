from rest_framework import serializers

from daiquiri.jobs.serializers import SyncJobSerializer


class SyncDatalinkJobSerializer(SyncJobSerializer):

    RESPONSEFORMAT = serializers.CharField(required=False)
    FORMAT = serializers.CharField(required=False)
