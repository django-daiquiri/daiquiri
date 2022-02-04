from daiquiri.core.serializers import JSONListField
from daiquiri.metadata.models import Schema, Table
from django.conf import settings
from django.urls import reverse
from rest_framework import serializers


class DublincoreSerializer(serializers.Serializer):

    title = serializers.CharField()
    creators = serializers.ReadOnlyField(default={'name': settings.SITE_CREATOR})
    subjects = serializers.ReadOnlyField(default=settings.SITE_SUBJECTS)
    publisher = serializers.ReadOnlyField(default=settings.SITE_PUBLISHER)
    date = serializers.CharField(default=settings.SITE_CREATED)
    identifier = serializers.CharField(source='doi')
    rights = serializers.CharField(default=settings.LICENSE_URLS.get('CC0'))


class DataciteSerializer(serializers.Serializer):

    identifier = serializers.CharField(source='doi')
    creators = serializers.ReadOnlyField(default=[
        {
            'name': settings.SITE_CREATOR
        }
    ])
    title = serializers.CharField()
    publisher = serializers.ReadOnlyField(default=settings.SITE_PUBLISHER)
    publication_year = serializers.CharField(default=settings.SITE_CREATED.split('-')[0])
    subjects = serializers.ReadOnlyField(default=settings.SITE_SUBJECTS)
    updated = serializers.CharField(default=settings.SITE_UPDATED)
    language = serializers.ReadOnlyField(default=settings.SITE_LANGUAGE)
    formats = serializers.ListField()
    license = serializers.CharField(default='CC0')
    license_url = serializers.CharField(default=settings.LICENSE_URLS.get('CC0'))
    resource_type = serializers.CharField(default='Dataset')
    alternate_identifiers = serializers.ReadOnlyField(default=[])
    related_identifiers = serializers.ReadOnlyField(default=[])
