from django.conf import settings

from rest_framework import serializers

from daiquiri.core.serializers import JSONListField
from daiquiri.core.constants import LICENSE_URLS
from daiquiri.metadata.models import Schema, Table


class DataCiteSerializer(serializers.ModelSerializer):

    license_url = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    publication_year = serializers.SerializerMethodField()
    resource_type = serializers.SerializerMethodField()

    language = serializers.ReadOnlyField(default=settings.METADATA_LANGUAGE)
    publisher = serializers.ReadOnlyField(default=settings.METADATA_PUBLISHER)

    creators = JSONListField(default=[])
    contributors = JSONListField(default=[])

    def get_license_url(self, obj):
        return LICENSE_URLS.get(obj.license)

    def get_size(self, obj):
        raise NotImplementedError()

    def get_publication_year(self, obj):
        return obj.published.year if obj.published else None


class SchemaSerializer(DataCiteSerializer):

    class Meta:
        model = Schema
        fields = (
            'name',
            'title',
            'description',
            'long_description',
            'license',
            'doi',
            'creators',
            'contributors',
            'published',
            'updated',
            'license_url',
            'size',
            'publication_year',
            'language',
            'publisher',
            'resource_type',
        )

    def get_resource_type(self, obj):
        return 'Database schema'

    def get_size(self, obj):
        tables = obj.tables.filter_by_metadata_access_level(self.context['request'].user)
        return '%i tables' % tables.count()


class TableSerializer(DataCiteSerializer):

    class Meta:
        model = Table
        fields = (
            'name',
            'title',
            'description',
            'long_description',
            'license',
            'doi',
            'creators',
            'contributors',
            'published',
            'updated',
            'license_url',
            'size',
            'publication_year',
            'language',
            'publisher',
            'resource_type',
        )

    def get_resource_type(self, obj):
        return 'Database table'

    def get_size(self, obj):
        columns = obj.columns.filter_by_metadata_access_level(self.context['request'].user)
        return '%i columns' % columns.count()
