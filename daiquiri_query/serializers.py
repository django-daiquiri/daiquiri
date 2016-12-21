from rest_framework import serializers

from daiquiri_metadata.models import Database, Table, Column, Function

from .models import QueryJob


class FormSerializer(serializers.Serializer):

    key = serializers.CharField()
    form_service = serializers.SerializerMethodField()

    def get_form_service(self, obj):
        return obj['key'][0].upper() + obj['key'][1:] + 'FormService'


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
        fields = '__all__'


class QueryJobCreateSerializer(serializers.ModelSerializer):

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


class FunctionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Function
        fields = (
            'id',
            'order',
            'name',
            'description'
        )


class ColumnSerializer(serializers.ModelSerializer):

    class Meta:
        model = Column
        fields = (
            'id',
            'order',
            'name',
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
            'description',
            'utype',
            'tables'
        )
