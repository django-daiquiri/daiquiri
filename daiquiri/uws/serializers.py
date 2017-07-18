from rest_framework import serializers

from daiquiri.jobs.models import Job


class UWSJobListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Job
        fields = ('id', 'phase')


class UWSJobRetrieveSerializer(serializers.ModelSerializer):

    job_id = serializers.UUIDField(source='id')
    owner_id = serializers.UUIDField(source='owner.username')
    destruction = serializers.DateTimeField(source='destruction_time')

    class Meta:
        model = Job
        fields = (
            'job_id',
            'owner_id',
            'phase',
            'quote',
            'start_time',
            'end_time',
            'execution_duration',
            'destruction',
            'results',
            'parameters'
        )


class UWSJobCreateSerializer(serializers.Serializer):

    PHASE = serializers.CharField(required=False)


class UWSJobUpdateSerializer(serializers.Serializer):

    PHASE = serializers.CharField(required=False)
