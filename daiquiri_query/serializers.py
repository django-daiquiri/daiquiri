from rest_framework import serializers

from daiquiri_metadata.models import Database, Table, Column, Function

from .models import QueryJob


class QueryJobSerializer(serializers.ModelSerializer):

    class Meta:
        model = QueryJob
        fields = '__all__'


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
