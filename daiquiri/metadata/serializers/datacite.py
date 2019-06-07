from django.conf import settings

from rest_framework import serializers

from daiquiri.core.serializers import JSONListField
from daiquiri.core.constants import LICENSE_URLS
from daiquiri.metadata.models import Schema, Table


class DataciteSerializer(serializers.ModelSerializer):

    identifier = serializers.SerializerMethodField()
    creators = JSONListField(default=[])
    title = serializers.SerializerMethodField()
    publisher = serializers.ReadOnlyField(default=settings.METADATA_PUBLISHER)
    publication_year = serializers.SerializerMethodField()
    subjects = serializers.ReadOnlyField(default=settings.METADATA_SUBJECTS)
    contributors = JSONListField(default=[])
    language = serializers.ReadOnlyField(default=settings.METADATA_LANGUAGE)
    resource_type = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    license_url = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    def get_title(self, obj):
        return obj.title or obj.name

    def get_publication_year(self, obj):
        return obj.published.year if obj.published else None

    def get_size(self, obj):
        raise NotImplementedError()

    def get_license_url(self, obj):
        return LICENSE_URLS.get(obj.license)

    def get_description(self, obj):
        return obj.long_description or obj.description


class SchemaDataciteSerializer(DataciteSerializer):

    class Meta:
        model = Schema
        fields = (
            'identifier',
            'creators',
            'title',
            'publisher',
            'publication_year',
            'subjects',
            'contributors',
            'updated',
            'language',
            'resource_type',
            'size',
            'license',
            'license_url',
            'description',
        )

    def get_identifier(self, obj):
        return obj.doi or 'schemas/%i' % obj.pk

    def get_resource_type(self, obj):
        return 'Database schema'

    def get_size(self, obj):
        tables = obj.tables.filter_by_metadata_access_level(self.context['request'].user)
        return '%i tables' % tables.count()


class TableDataciteSerializer(DataciteSerializer):

    class Meta:
        model = Table
        fields = '__all__'
        fields = (
            'identifier',
            'creators',
            'title',
            'publisher',
            'publication_year',
            'subjects',
            'contributors',
            'updated',
            'language',
            'resource_type',
            'size',
            'license',
            'license_url',
            'description',
        )

    def get_identifier(self, obj):
        return obj.doi or 'tables/%i' % obj.pk

    def get_resource_type(self, obj):
        return 'Database table'

    def get_size(self, obj):
        # filter the columns which are published for the groups of the user
        if not settings.METADATA_COLUMN_PERMISSIONS:
            columns = obj.columns.all()
        else:
            columns = obj.columns.filter_by_access_level(self.context['request'].user)
        return '%i columns' % columns.count()
