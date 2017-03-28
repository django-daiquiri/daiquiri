from rest_framework import serializers

from django.contrib.auth.models import Group

from daiquiri_metadata.models import Database, Table, Column, Function

from .models import QueryJob, Example


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
            'actual_query',
            'queue',
            'nrows',
            'size'
        )


class QueryJobCreateSerializer(serializers.ModelSerializer):

    query = serializers.CharField(required=False)
    table_name = serializers.CharField(required=False)

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


class FunctionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Function
        fields = (
            'id',
            'order',
            'name',
            'query_string'
        )


class ColumnSerializer(serializers.ModelSerializer):

    class Meta:
        model = Column
        fields = (
            'id',
            'order',
            'name',
            'query_string',
            'description',
            'unit',
            'ucd',
            'utype',
            'datatype',
            'size',
            'principal',
            'indexed',
            'std'
        )


class TableSerializer(serializers.ModelSerializer):

    columns = ColumnSerializer(many=True, read_only=True)

    class Meta:
        model = Table
        fields = (
            'id',
            'order',
            'name',
            'query_string',
            'description',
            'type',
            'utype',
            'columns'
        )


class DatabaseSerializer(serializers.ModelSerializer):

    tables = TableSerializer(many=True, read_only=True)

    class Meta:
        model = Database
        fields = (
            'id',
            'order',
            'name',
            'query_string',
            'description',
            'utype',
            'tables'
        )

class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = ('id', 'name')