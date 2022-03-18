from rest_framework import serializers

from daiquiri.core.serializers import CaseInsensitiveSerializer
from daiquiri.jobs.models import Job

from .utils import get_job_results


class JobListSerializer(serializers.ModelSerializer):

    creation_time = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = ('id', 'phase', 'run_id', 'creation_time')

    def get_creation_time(self, obj):
        return obj.creation_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ') if obj.creation_time else None


class JobRetrieveSerializer(serializers.ModelSerializer):

    job_id = serializers.UUIDField(source='id')
    owner_id = serializers.SerializerMethodField()
    destruction = serializers.DateTimeField(source='destruction_time')
    results = serializers.SerializerMethodField()

    creation_time = serializers.SerializerMethodField()
    start_time = serializers.SerializerMethodField()
    end_time = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = (
            'job_id',
            'run_id',
            'owner_id',
            'phase',
            'quote',
            'creation_time',
            'start_time',
            'end_time',
            'execution_duration',
            'destruction',
            'error_summary',
            'results',
            'parameters'
        )

    def get_owner_id(self, obj):
        if obj.owner:
            return obj.owner.username
        else:
            return None

    def get_results(self, obj):
        return get_job_results(self.context['request'], obj)

    def get_creation_time(self, obj):
        return obj.creation_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ') if obj.creation_time else None

    def get_start_time(self, obj):
        return obj.start_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ') if obj.start_time else None

    def get_end_time(self, obj):
        return obj.end_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ') if obj.end_time else None


class JobUpdateSerializer(CaseInsensitiveSerializer):

    ACTION = serializers.CharField(required=False)
    DESTRUCTION = serializers.DateTimeField(required=False)
    EXECUTIONDURATION = serializers.IntegerField(required=False)
    PHASE = serializers.CharField(required=False)


class SyncJobSerializer(CaseInsensitiveSerializer):

    RESPONSEFORMAT = serializers.CharField(required=False)
    MAXREC = serializers.IntegerField(required=False)
    RUNID = serializers.CharField(required=False, default='')


class AsyncJobSerializer(CaseInsensitiveSerializer):

    PHASE = serializers.CharField(required=False)
    RESPONSEFORMAT = serializers.CharField(required=False)
    MAXREC = serializers.IntegerField(required=False)
    RUNID = serializers.CharField(required=False, default='')
