from django.conf import settings

from rest_framework import serializers

from daiquiri.core.serializers import JSONField
from daiquiri.core.constants import LICENSE_URLS

from ..models import Schema, Table


class SchemaSerializer(serializers.ModelSerializer):

    license_url = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    publication_year = serializers.SerializerMethodField()

    language = serializers.ReadOnlyField(default=settings.METADATA_LANGUAGE)
    publisher = serializers.ReadOnlyField(default=settings.METADATA_PUBLISHER)
    resource_type = serializers.ReadOnlyField(default='Database schema')

    creators = JSONField(allow_null=True)
    contributors = JSONField(allow_null=True)

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

    def get_license_url(self, obj):
        return LICENSE_URLS.get(obj.license)

    def get_size(self, obj):
        return '%i tables' % obj.tables.count()

    def get_publication_year(self, obj):
        return obj.published.year if obj.published else None
