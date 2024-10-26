from django.conf import settings
from django.contrib.auth.models import Group

from daiquiri.core.serializers import JSONListField

from rest_framework import serializers

from .validators import PersonListValidator
from ..models import Schema, Table, Column, Function


class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = ('id', 'name')


class FunctionSerializer(serializers.ModelSerializer):

    label = serializers.CharField(source='__str__', read_only=True)
    admin_url = serializers.CharField(read_only=True)

    class Meta:
        model = Function
        fields = '__all__'


class ColumnSerializer(serializers.ModelSerializer):

    label = serializers.CharField(source='__str__', read_only=True)
    admin_url = serializers.CharField(read_only=True)

    class Meta:
        model = Column

        # only show access_level, metadata_access_level, and groups when
        # settings.METADATA_COLUMN_PERMISSIONS is set
        if settings.METADATA_COLUMN_PERMISSIONS:
            fields = '__all__'
        else:
            fields = (
                'id',
                'label',
                'order',
                'name',
                'description',
                'unit',
                'ucd',
                'utype',
                'datatype',
                'arraysize',
                'index_for',
                'principal',
                'indexed',
                'std',
                'table',
                'admin_url'
            )


class TableSerializer(serializers.ModelSerializer):

    label = serializers.CharField(source='__str__', read_only=True)

    related_identifiers = JSONListField(required=False)
    creators = JSONListField(required=False, validators=[PersonListValidator()])
    contributors = JSONListField(required=False, validators=[PersonListValidator()])
    license = serializers.ChoiceField(choices=settings.LICENSE_CHOICES, default='')
    admin_url = serializers.CharField(read_only=True)

    class Meta:
        model = Table
        fields = '__all__'


class SchemaSerializer(serializers.ModelSerializer):

    label = serializers.CharField(source='__str__', read_only=True)

    related_identifiers = JSONListField(required=False)
    creators = JSONListField(required=False, validators=[PersonListValidator()])
    contributors = JSONListField(required=False, validators=[PersonListValidator()])
    license = serializers.ChoiceField(choices=settings.LICENSE_CHOICES, default='', initial='')
    admin_url = serializers.CharField(read_only=True)

    class Meta:
        model = Schema
        fields = '__all__'
