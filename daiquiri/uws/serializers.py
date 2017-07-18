from rest_framework import serializers

from daiquiri.jobs.models import Job


class JobListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Job
        fields = ('id', 'phase')


class JobRetrieveSerializer(serializers.ModelSerializer):

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


class JobCreateSerializer(serializers.Serializer):

    PHASE = serializers.CharField(required=False)


class JobUpdateSerializer(serializers.Serializer):

    PHASE = serializers.CharField(required=False)


from daiquiri.query.validators import (
    validate_table_name,
    validate_queue,
    validate_query_language
)

class QueryJobCreateSerializer(JobCreateSerializer):

    TABLE_NAME = serializers.CharField(required=False, validators=[validate_table_name])
    QUEUE = serializers.CharField(required=False, validators=[validate_queue])
    LANG = serializers.CharField(source='query_language', validators=[validate_query_language])
    QUERY = serializers.CharField(source='query')
