from django.template.loader import TemplateDoesNotExist, get_template

from rest_framework import serializers

from daiquiri.jobs.serializers import AsyncJobSerializer, SyncJobSerializer

from .models import Example, QueryJob
from .utils import get_query_form, get_query_form_adapter
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
    template = serializers.SerializerMethodField(required=False)
    fields = serializers.SerializerMethodField(method_name='get_adapter_fields')
    submit = serializers.CharField(default=None)

    def get_template(self, obj):
        try:
            return get_template(obj['template']).render(request=self.context.get('request')).strip()
        except (KeyError, TemplateDoesNotExist):
            return None

    def get_adapter_fields(self, obj):
        adapter = get_query_form_adapter(obj)
        return adapter.get_fields() if adapter else None


class DropdownSerializer(serializers.Serializer):

    key = serializers.CharField()
    label = serializers.CharField()
    classes = serializers.CharField(default=None)
    options = serializers.JSONField(default=None)


class DownloadSerializer(serializers.Serializer):

    key = serializers.CharField()
    form = serializers.JSONField(default=None)


class QueryJobSerializer(serializers.ModelSerializer):

    class Meta:
        model = QueryJob
        fields = (
            'id',
        )


class QueryJobIndexSerializer(serializers.ModelSerializer):

    class Meta:
        model = QueryJob
        fields = (
            'id',
            'table_name',
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
            'phase_label',
            'creation_time',
            'creation_time_label',
            'start_time',
            'start_time_label',
            'end_time',
            'end_time_label',
            'execution_duration',
            'time_queue',
            'time_query',
            'destruction_time',
            'error_summary',
            'job_type',
            'schema_name',
            'table_name',
            'query_language',
            'query_language_label',
            'query',
            'native_query',
            'actual_query',
            'queue',
            'result_status',
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


class QueryJobFormSerializer(QueryJobCreateSerializer):

    query_language = serializers.SerializerMethodField()
    query = serializers.SerializerMethodField()

    class Meta:
        model = QueryJob
        fields = QueryJobCreateSerializer.Meta.fields

    def __init__(self, *args, **kwargs):
        form_key = kwargs.pop('form_key')
        form = get_query_form(form_key)

        self.adapter = get_query_form_adapter(form)

        super().__init__(*args, **kwargs)

        for field in self.adapter.get_fields():
            if field.get('type') == 'number':
                self.fields[field['key']] = serializers.FloatField(required=True)
            else:
                self.fields[field['key']] = serializers.CharField(required=False)

    def get_query_language(self, obj):
        return self.adapter.get_query_language(obj)

    def get_query(self, obj):
        return self.adapter.get_query(obj)


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
        return '{key}-{version}'.format(**obj)



class QueryDownloadFormatSerializer(serializers.Serializer):

    key = serializers.CharField()
    extension = serializers.CharField()
    content_type = serializers.CharField()
    label = serializers.CharField()
    help = serializers.CharField()



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
