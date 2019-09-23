from django.conf import settings

from rest_framework import serializers

from daiquiri.core.serializers import JSONListField
from daiquiri.metadata.models import Schema, Table


class DublincoreSerializer(serializers.ModelSerializer):

    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    creators = JSONListField(default=[])
    contributors = JSONListField(default=[])
    subjects = serializers.ReadOnlyField(default=settings.SITE_SUBJECTS)
    publisher = serializers.ReadOnlyField(default=settings.SITE_PUBLISHER)
    date = serializers.ReadOnlyField(source='published')
    type = serializers.SerializerMethodField()
    identifier = serializers.SerializerMethodField()
    rights = serializers.ReadOnlyField(source='license')

    def get_title(self, obj):
        return obj.title or obj.name

    def get_description(self, obj):
        return obj.long_description or obj.description

    def get_type(self, obj):
        return 'Dataset'

    def get_identifier(self, obj):
        raise NotImplementedError()


class DublincoreSchemaSerializer(DublincoreSerializer):

    class Meta:
        model = Schema
        fields = (
            'title',
            'description',
            'creators',
            'contributors',
            'subjects',
            'publisher',
            'date',
            'type',
            'identifier',
            'rights'
        )

    def get_identifier(self, obj):
        return obj.doi or 'schemas/%i' % obj.pk


class DublincoreTableSerializer(DublincoreSerializer):

    class Meta:
        model = Table
        fields = (
            'title',
            'description',
            'creators',
            'contributors',
            'subjects',
            'publisher',
            'date',
            'type',
            'identifier',
            'rights'
        )

    def get_identifier(self, obj):
        return obj.doi or 'tables/%i' % obj.pk
