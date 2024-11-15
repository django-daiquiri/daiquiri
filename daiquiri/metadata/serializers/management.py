from rest_framework import serializers

from ..models import Column, Function, Schema, Table


class ColumnSerializer(serializers.ModelSerializer):

    class Meta:
        model = Column
        fields = ('id', 'name')


class TableSerializer(serializers.ModelSerializer):

    columns = ColumnSerializer(many=True, read_only=True)

    class Meta:
        model = Table
        fields = ('id', 'name', 'columns')


class SchemaSerializer(serializers.ModelSerializer):

    tables = TableSerializer(many=True, read_only=True)

    class Meta:
        model = Schema
        fields = ('id', 'name', 'tables')


class FunctionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Function
        fields = ('id', 'name')
