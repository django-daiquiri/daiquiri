from rest_framework import serializers

from daiquiri.uws.serializers import UWSJobCreateSerializer

from .models import QueryJob, Example
from .validators import validate_table_name, validate_query_language, validate_queue


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
            'size'
        )


class QueryJobCreateSerializer(serializers.ModelSerializer):

    table_name = serializers.CharField(required=False, allow_blank=True, validators=[validate_table_name])
    queue = serializers.CharField(required=False, validators=[validate_queue])
    query_language = serializers.CharField(required=True, validators=[validate_query_language])
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

    table_name = serializers.CharField(required=True, validators=[validate_table_name])

    class Meta:
        model = QueryJob
        fields = (
            'id',
            'table_name'
        )


class ExampleSerializer(serializers.ModelSerializer):

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


class UWSQueryJobCreateSerializer(UWSJobCreateSerializer):

    TABLE_NAME = serializers.CharField(required=False, validators=[validate_table_name])
    QUEUE = serializers.CharField(required=False, validators=[validate_queue])
    LANG = serializers.CharField(required=True, validators=[validate_query_language])
    QUERY = serializers.CharField(required=True)
