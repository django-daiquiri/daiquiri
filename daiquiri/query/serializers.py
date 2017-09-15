from rest_framework import serializers

from daiquiri.jobs.serializers import SyncJobSerializer, AsyncJobSerializer

from .models import QueryJob, Example
from .validators import TableNameValidator, QueryLanguageValidator, QueueValidator, ResponseFormatValidator


class FormSerializer(serializers.Serializer):

    key = serializers.CharField()
    form_service = serializers.SerializerMethodField()

    def get_form_service(self, obj):
        return obj['key'][0].upper() + obj['key'][1:] + 'FormService'


class DropdownSerializer(serializers.Serializer):

    key = serializers.CharField()
    dropdown_service = serializers.SerializerMethodField()
    options = serializers.SerializerMethodField()

    def get_dropdown_service(self, obj):
        return obj['key'][0].upper() + obj['key'][1:] + 'DropdownService'

    def get_options(self, obj):
        return obj['options']


class QueryJobSerializer(serializers.ModelSerializer):

    class Meta:
        model = QueryJob
        fields = (
            'id',
        )


class QueryJobListSerializer(serializers.ModelSerializer):

    class Meta:
        model = QueryJob
        fields = (
            'id',
            'table_name',
            'creation_time',
            'phase'
        )


class QueryJobRetrieveSerializer(serializers.ModelSerializer):

    columns = serializers.SerializerMethodField()

    class Meta:
        model = QueryJob
        fields = (
            'id',
            'run_id',
            'phase',
            'creation_time',
            'start_time',
            'end_time',
            'execution_duration',
            'time_queue',
            'time_query',
            'destruction_time',
            'error_summary',
            'job_type',
            'database_name',
            'table_name',
            'query_language',
            'query',
            'native_query',
            'actual_query',
            'queue',
            'nrows',
            'size',
            'columns'
        )

    def get_columns(self, obj):
        if 'columns' in obj.metadata:
            return obj.metadata['columns']
        else:
            return []


class QueryJobCreateSerializer(serializers.ModelSerializer):

    table_name = serializers.CharField(required=False, allow_blank=True, validators=[TableNameValidator()])
    queue = serializers.CharField(required=False, validators=[QueueValidator()])
    query_language = serializers.CharField(required=True, validators=[QueryLanguageValidator()])
    query = serializers.CharField(required=True)

    class Meta:
        model = QueryJob
        fields = (
            'id',
            'table_name',
            'queue',
            'query_language',
            'query'
        )


class QueryJobUpdateSerializer(serializers.ModelSerializer):

    table_name = serializers.CharField(required=True, validators=[TableNameValidator()])

    class Meta:
        model = QueryJob
        fields = (
            'id',
            'table_name'
        )


class QueryLanguageSerializer(serializers.Serializer):

    id = serializers.SerializerMethodField(required=False)
    text = serializers.CharField(source='label')
    quote_char = serializers.CharField()

    def get_id(self, obj):
        return '%(key)s-%(version)s' % obj


class ExampleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Example
        fields = (
            'id',
            'order',
            'name',
            'description',
            'query_language',
            'query_string',
            'access_level',
            'groups'
        )


class UserExampleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Example
        fields = (
            'id',
            'order',
            'name',
            'description',
            'query_string',
            'groups'
        )


class SyncQueryJobSerializer(SyncJobSerializer):

    RESPONSEFORMAT = serializers.CharField(required=False, validators=[ResponseFormatValidator()])
    FORMAT = serializers.CharField(required=False, validators=[ResponseFormatValidator()])

    TABLE_NAME = serializers.CharField(required=False, validators=[TableNameValidator()])
    LANG = serializers.CharField(required=True, validators=[QueryLanguageValidator()])
    QUERY = serializers.CharField(required=True)


class AsyncQueryJobSerializer(AsyncJobSerializer):

    RESPONSEFORMAT = serializers.CharField(required=False, validators=[ResponseFormatValidator()])
    FORMAT = serializers.CharField(required=False, validators=[ResponseFormatValidator()])

    TABLE_NAME = serializers.CharField(required=False, validators=[TableNameValidator()])
    QUEUE = serializers.CharField(required=False, validators=[QueueValidator()])
    LANG = serializers.CharField(required=True, validators=[QueryLanguageValidator()])
    QUERY = serializers.CharField(required=True)
