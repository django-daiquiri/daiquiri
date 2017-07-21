from rest_framework import serializers

from daiquiri.query.models import Example
from daiquiri.metadata.models import Database, Table, Column


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
        fields = (
            'name',
            'datatype',
            'ucd',
            'unit',
            'indexed',
            'principal',
            'std'
        )


class TableSerializer(serializers.ModelSerializer):

    columns = ColumnSerializer(many=True)

    class Meta:
        model = Table
        fields = (
            'name',
            'description',
            'columns'
        )


class SchemaSerializer(serializers.ModelSerializer):

    tables = TableSerializer(many=True)

    class Meta:
        model = Database
        fields = (
            'name',
            'description',
            'tables'
        )
