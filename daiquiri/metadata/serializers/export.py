from django.conf import settings

from rest_framework import serializers

from ..models import Column, Function, Schema, Table


class ColumnSerializer(serializers.ModelSerializer):

    if settings.METADATA_COLUMN_PERMISSIONS:
        groups = serializers.SerializerMethodField()

    class Meta:
        model = Column

        # only show access_level, metadata_access_level, and groups when
        # settings.METADATA_COLUMN_PERMISSIONS is set
        if settings.METADATA_COLUMN_PERMISSIONS:
            fields = (
                'order',
                'name',
                'description',
                'unit',
                'ucd',
                'utype',
                'principal',
                'std',
                'access_level',
                'metadata_access_level',
                'groups'
            )
        else:
            fields = (
                'order',
                'name',
                'description',
                'unit',
                'ucd',
                'utype',
                'principal',
                'std'
            )

    def get_groups(self, obj):
        return [group.name for group in obj.groups.all()]


class TableSerializer(serializers.ModelSerializer):

    groups = serializers.SerializerMethodField()
    columns = ColumnSerializer(many=True, read_only=True)

    class Meta:
        model = Table
        fields = (
            'order',
            'name',
            'title',
            'description',
            'long_description',
            'attribution',
            'license',
            'doi',
            'type',
            'utype',
            'access_level',
            'metadata_access_level',
            'groups',
            'columns'
        )

    def get_groups(self, obj):
        return [group.name for group in obj.groups.all()]


class SchemaSerializer(serializers.ModelSerializer):

    groups = serializers.SerializerMethodField()
    tables = TableSerializer(many=True, read_only=True)

    class Meta:
        model = Schema
        fields = (
            'order',
            'name',
            'title',
            'description',
            'long_description',
            'attribution',
            'license',
            'doi',
            'utype',
            'access_level',
            'metadata_access_level',
            'groups',
            'tables'
        )

    def get_groups(self, obj):
        return [group.name for group in obj.groups.all()]


class FunctionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Function
        fields = (
            'order',
            'name',
            'query_string'
        )
