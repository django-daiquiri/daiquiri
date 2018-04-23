from django.conf import settings

from rest_framework import serializers

from daiquiri.metadata.models import Schema, Table, Column


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
            'columns',
            'doi',
            'nrows'
        )

    def get_columns(self, obj):
        # filter the columns which are published for the groups of the user
        if settings.METADATA_COLUMN_PERMISSIONS:
            queryset = obj.columns.filter_by_access_level(self.context['request'].user)
        else:
            queryset = obj.columns.all()

        return ColumnSerializer(queryset, context=self.context, many=True).data


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
        queryset = obj.tables.filter_by_access_level(self.context['request'].user)
        return TableSerializer(queryset, context=self.context, many=True).data
