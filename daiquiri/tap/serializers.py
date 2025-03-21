from rest_framework import serializers

from daiquiri.core.constants import ACCESS_LEVEL_PUBLIC
from daiquiri.metadata.models import Column, Schema, Table


class ColumnSerializer(serializers.ModelSerializer):

    class Meta:
        model = Column
        fields = (
            'name',
            'description',
            'datatype',
            'ucd',
            'unit',
            'indexed',
            'principal',
            'std'
        )


class TableSerializer(serializers.ModelSerializer):

    name = serializers.SerializerMethodField()
    columns = ColumnSerializer(many=True)

    class Meta:
        model = Table
        fields = (
            'name',
            'description',
            'columns',
            'doi',
            'nrows'
        )

    def get_name(self, obj):
        return str(obj)


class SchemaSerializer(serializers.ModelSerializer):

    tables = serializers.SerializerMethodField()

    class Meta:
        model = Schema
        fields = (
            'name',
            'description',
            'tables'
        )

    def get_tables(self, obj):
        # filter the tables which are published for the groups of the user
        queryset = obj.tables.filter(metadata_access_level=ACCESS_LEVEL_PUBLIC, published__isnull=False)
        return TableSerializer(queryset, many=True).data
