from rest_framework import serializers

from ..models import Schema, Table, Column, Function


class ColumnSerializer(serializers.ModelSerializer):

    type = serializers.CharField(default='column')

    class Meta:
        model = Column
        fields = ('id', 'type', 'name')


class TableSerializer(serializers.ModelSerializer):

    type = serializers.CharField(default='table')

    columns = ColumnSerializer(many=True, read_only=True)



    class Meta:
        model = Table
        fields = ('id', 'type', 'name', 'columns')


class SchemaSerializer(serializers.ModelSerializer):

    type = serializers.CharField(default='schema')

    tables = TableSerializer(many=True, read_only=True)

    class Meta:
        model = Schema
        fields = ('id', 'type', 'name', 'tables')


class FunctionSerializer(serializers.ModelSerializer):

    type = serializers.CharField(default='function')

    class Meta:
        model = Function
        fields = ('id', 'type', 'name')
