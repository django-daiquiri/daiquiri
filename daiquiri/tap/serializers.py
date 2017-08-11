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

    columns = serializers.SerializerMethodField()

    class Meta:
        model = Table
        fields = (
            'name',
            'description',
            'columns'
        )

    def get_columns(self, obj):
        # filter the columns which are published for the groups of the user
        queryset = obj.columns.filter_by_access_level(self.context['request'].user)
        return ColumnSerializer(queryset, context=self.context, many=True).data


class SchemaSerializer(serializers.ModelSerializer):

    tables = serializers.SerializerMethodField()

    class Meta:
        model = Database
        fields = (
            'name',
            'description',
            'tables'
        )

    def get_tables(self, obj):
        # filter the tables which are published for the groups of the user
        queryset = obj.tables.filter_by_access_level(self.context['request'].user)
        return TableSerializer(queryset, context=self.context, many=True).data
