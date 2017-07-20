from rest_framework import serializers

from daiquiri.query.models import Example
from .models import Schema, Table, Column


class ExampleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Example
        fields = (
            'id',
            'name',
            'description',
            'query_string'
        )


class ColumnSerializer(serializers.ModelSerializer):

    class Meta:
        model = Column
        fields = '__all__'


class TableSerializer(serializers.ModelSerializer):

    columns = ColumnSerializer(many=True)

    class Meta:
        model = Table
        fields = '__all__'


class SchemaSerializer(serializers.ModelSerializer):

    tables = TableSerializer(many=True)

    class Meta:
        model = Schema
        fields = '__all__'
