from daiquiri.core.constants import LICENSE_URLS
from daiquiri.core.serializers import JSONListField
from daiquiri.metadata.models import Schema, Table
from django.conf import settings
from django.urls import reverse
from rest_framework import serializers


class DataciteSerializer(serializers.ModelSerializer):

    identifier = serializers.SerializerMethodField()
    creators = JSONListField(default=[])
    title = serializers.SerializerMethodField()
    publisher = serializers.ReadOnlyField(default=settings.SITE_PUBLISHER)
    publication_year = serializers.SerializerMethodField()
    subjects = serializers.ReadOnlyField(default=settings.SITE_SUBJECTS)
    contributors = JSONListField(default=[])
    language = serializers.ReadOnlyField(default=settings.SITE_LANGUAGE)
    alternate_identifiers = serializers.SerializerMethodField()
    related_identifiers = serializers.SerializerMethodField() 
    resource_type = serializers.SerializerMethodField()
    formats = serializers.SerializerMethodField()
    sizes = serializers.SerializerMethodField()
    license_url = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    def get_publication_year(self, obj):
        return obj.published.year if obj.published else None

    def get_alternate_identifiers(self, obj):
        raise NotImplementedError()

    def get_related_identifiers(self, obj):
        '''Abstract method (should be overwritten by child class)
        '''
        raise NotImplementedError()

    def get_formats(self, obj):
        if hasattr(settings, 'QUERY_DOWNLOAD_FORMATS'):
            return [f['content_type'] for f in settings.QUERY_DOWNLOAD_FORMATS]
        else:
            return []

    def get_sizes(self, obj):
        raise NotImplementedError()

    def get_license_url(self, obj):
        return LICENSE_URLS.get(obj.license)

    def get_description(self, obj):
        return obj.long_description or obj.description


class DataciteSchemaSerializer(DataciteSerializer):

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
            'alternate_identifiers',
            'sizes',
            'formats',
            'license',
            'license_url',
            'description',
        )

    def get_title(self, obj):
        return obj.title or obj.name

    def get_identifier(self, obj):
        return obj.doi or 'schemas/%i' % obj.pk

    def get_alternate_identifiers(self, obj):
        url = self.context['request'].build_absolute_uri(reverse('metadata:schema', args=[obj.name]))
        return [{
            'alternate_identifier': url,
            'alternate_identifier_type': 'URL'
        }]

    def get_resource_type(self, obj):
        return 'Database schema'

    def get_sizes(self, obj):
        tables = obj.tables.filter_by_metadata_access_level(self.context['request'].user)
        return ['%i tables' % tables.count()]


class DataciteTableSerializer(DataciteSerializer):

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
            'alternate_identifiers',
            'related_identifiers',
            'sizes',
            'formats',
            'license',
            'license_url',
            'description',
        )

    def get_title(self, obj):
        return obj.title or '%s.%s' % (obj.schema.name, obj.name)

    def get_identifier(self, obj):
        return obj.doi or 'tables/%i' % obj.pk
    
    def get_resource_type(self, obj):
        return 'Database table'

    def get_alternate_identifiers(self, obj):
        url = self.context['request'].build_absolute_uri(reverse('metadata:table', args=[obj.schema.name, obj.name]))
        return [{
            'alternate_identifier': url,
            'alternate_identifier_type': 'URL'
        }]

    def get_related_identifiers(self, obj):
        '''Returns an array of json-like dict with the related_identifiers and their parameters.
        '''
        schema_doi = obj.schema.doi
        return [{'related_identifier': schema_doi,
                 'related_identifier_type': 'DOI',
                 'relation_type': 'IsPartOf'}]

    def get_sizes(self, obj):
        # filter the columns which are published for the groups of the user
        if not settings.METADATA_COLUMN_PERMISSIONS:
            columns = obj.columns.all()
        else:
            columns = obj.columns.filter_by_access_level(self.context['request'].user)

        return ['%i columns' % columns.count(), '%i rows' % (obj.nrows or 0)]
