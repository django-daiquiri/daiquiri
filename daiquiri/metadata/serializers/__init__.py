from django.conf import settings
from django.contrib.auth.models import Group

from rest_framework import serializers

from daiquiri.core.serializers import JSONListField
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator

from ..models import Column, Function, Schema, Table
from .validators import PersonListValidator
from daiquiri.query.validators import TableNameValidator


class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = ('id', 'name')


class FunctionSerializer(serializers.ModelSerializer):

    label = serializers.CharField(source='__str__', read_only=True)

    name = serializers.CharField(validators=[TableNameValidator(),
        UniqueValidator(queryset=Function.objects.all(), lookup='iexact')])
    admin_url = serializers.CharField(read_only=True)

    class Meta:
        model = Function
        fields = '__all__'


class ColumnSerializer(serializers.ModelSerializer):

    label = serializers.CharField(source='__str__', read_only=True)

    name = serializers.CharField(validators=[TableNameValidator()])
    width = serializers.IntegerField(source='get_width', read_only=True)
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
                'principal',
                'indexed',
                'std',
                'table',
                'admin_url',
                'width',
            )

    def validate(self, data):
        table = data.get('table')
        name = data.get('name')

        qs = Column.objects.filter(table=table, name__iexact=name)

        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise serializers.ValidationError({
                'name': 'This column already exists in this table.'
            })

        return data

class TableSerializer(serializers.ModelSerializer):

    label = serializers.CharField(source='__str__', read_only=True)

    name = serializers.CharField(validators=[TableNameValidator()])
    related_identifiers = JSONListField(required=False)
    creators = JSONListField(required=False, validators=[PersonListValidator()])
    contributors = JSONListField(required=False, validators=[PersonListValidator()])
    license = serializers.ChoiceField(choices=settings.LICENSE_CHOICES, default='')
    admin_url = serializers.CharField(read_only=True)

    class Meta:
        model = Table
        fields = '__all__'

    def validate(self, data):
        schema = data.get('schema')
        name = data.get('name')

        qs = Table.objects.filter(schema=schema, name__iexact=name)

        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise serializers.ValidationError({
                'name': 'This table already exists in this schema.'
            })

        return data

class SchemaSerializer(serializers.ModelSerializer):

    label = serializers.CharField(source='__str__', read_only=True)

    name = serializers.CharField(validators=[TableNameValidator(),
        UniqueValidator(queryset=Schema.objects.all(), lookup='iexact')])
    related_identifiers = JSONListField(required=False)
    creators = JSONListField(required=False, validators=[PersonListValidator()])
    contributors = JSONListField(required=False, validators=[PersonListValidator()])
    license = serializers.ChoiceField(choices=settings.LICENSE_CHOICES, default='', initial='')
    admin_url = serializers.CharField(read_only=True)

    class Meta:
        model = Schema
        fields = '__all__'
