from django.template.loader import get_template, TemplateDoesNotExist

from rest_framework import serializers

from daiquiri.jobs.serializers import SyncJobSerializer, AsyncJobSerializer
from .models import QueryJob, Example
from .validators import TableNameValidator, UploadFileValidator, UploadParamValidator


class FormListSerializer(serializers.Serializer):

    key = serializers.CharField()
    label = serializers.CharField()

    # TODO: remove
    form_service = serializers.SerializerMethodField()

    def get_form_service(self, obj):
        return obj['key'][0].upper() + obj['key'][1:] + 'FormService'


class FormDetailSerializer(serializers.Serializer):

    key = serializers.CharField()
    label = serializers.CharField()
    template = serializers.SerializerMethodField()

    def get_template(self, obj):
        try:
            return get_template(obj['template']).render(request=self.context.get('request')).strip()
        except (KeyError, TemplateDoesNotExist):
            return None


class DropdownSerializer(serializers.Serializer):

    key = serializers.CharField()
    label = serializers.CharField()
    options = serializers.JSONField()


class DownloadSerializer(serializers.Serializer):

    key = serializers.CharField()
    download_service = serializers.SerializerMethodField()
    options = serializers.SerializerMethodField()

    def get_download_service(self, obj):
        if obj.get('service'):
            return obj['key'][0].upper() + obj['key'][1:] + 'DownloadService'
        else:
            return None

    def get_options(self, obj):
        return obj.get('options', {})


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
            'run_id',
            'phase'
        )


class QueryJobRetrieveSerializer(serializers.ModelSerializer):

    sources = serializers.SerializerMethodField()
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
            'schema_name',
            'table_name',
            'query_language',
            'query',
            'native_query',
            'actual_query',
            'queue',
            'nrows',
            'size',
            'sources',
            'columns'
        )

    def get_sources(self, obj):
        if obj.metadata:
            return obj.metadata.get('sources', [])
        else:
            return []

    def get_columns(self, obj):
        if obj.metadata:
            return obj.metadata.get('columns', [])
        else:
            return []


class QueryJobCreateSerializer(serializers.ModelSerializer):

    table_name = serializers.CharField(required=False, allow_blank=True, max_length=256,
                                       validators=[TableNameValidator()])
    queue = serializers.CharField(required=False)
    query_language = serializers.CharField(required=True)
    query = serializers.CharField(required=True)
    run_id = serializers.CharField(default='', allow_blank=True)

    class Meta:
        model = QueryJob
        fields = (
            'id',
            'table_name',
            'queue',
            'query_language',
            'query',
            'run_id'
        )


class QueryJobUpdateSerializer(serializers.ModelSerializer):

    table_name = serializers.CharField(required=True, validators=[TableNameValidator()])

    class Meta:
        model = QueryJob
        fields = (
            'id',
            'table_name',
            'run_id'
        )


class QueryJobUploadSerializer(serializers.ModelSerializer):

    table_name = serializers.CharField(required=False, validators=[TableNameValidator()])
    run_id = serializers.CharField(default='')
    file = serializers.FileField(max_length=None, allow_empty_file=False, validators=[UploadFileValidator()])

    class Meta:
        model = QueryJob
        fields = (
            'table_name',
            'run_id',
            'file'
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
            'query_language',
            'groups'
        )


class SyncQueryJobSerializer(SyncJobSerializer):

    RESPONSEFORMAT = serializers.CharField(required=False)
    FORMAT = serializers.CharField(required=False)

    TABLE_NAME = serializers.CharField(required=False, max_length=256, validators=[TableNameValidator()])
    LANG = serializers.CharField(required=True)
    QUERY = serializers.CharField(required=True)

    UPLOAD = serializers.CharField(required=False, default='', validators=[UploadParamValidator()])


class AsyncQueryJobSerializer(AsyncJobSerializer):

    RESPONSEFORMAT = serializers.CharField(required=False)
    FORMAT = serializers.CharField(required=False)

    TABLE_NAME = serializers.CharField(required=False, max_length=256, validators=[TableNameValidator()])
    QUEUE = serializers.CharField(required=False)
    LANG = serializers.CharField(required=True)
    QUERY = serializers.CharField(required=True)

    UPLOAD = serializers.CharField(required=False, default='', validators=[UploadParamValidator()])
