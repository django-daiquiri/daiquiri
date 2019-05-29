from django.conf import settings

from rest_framework import serializers

from daiquiri.core.constants import LICENSE_URLS

from ..models import Schema, Table


class SchemaSerializer(serializers.ModelSerializer):

    license_url = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    publisher = serializers.ReadOnlyField(default=settings.METADATA_PUBLISHER)
    resource_type = serializers.ReadOnlyField(default='Database schema')

    class Meta:
        model = Schema
        fields = (
            'name',
            'title',
            'description',
            'long_description',
            'license',
            'license_url',
            'doi',
            'size',
            'publisher',
            'resource_type'
        )

    def get_license_url(self, obj):
        return LICENSE_URLS.get(obj.license)

    def get_size(self, obj):
        return '%i tables' % obj.tables.count()

    def get_publisher(self, obj):
        return settings.METADATA_PUBLISHER
