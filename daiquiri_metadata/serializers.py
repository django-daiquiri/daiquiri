from django.contrib.auth.models import Group

from rest_framework import serializers

from .models import Database, Table, Column, Function


class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = ('id', 'name')


class FunctionSerializer(serializers.ModelSerializer):

    label = serializers.CharField(source='__str__')

    class Meta:
        model = Function
        fields = '__all__'


class ColumnSerializer(serializers.ModelSerializer):

    label = serializers.CharField(source='__str__')

    class Meta:
        model = Column
        fields = '__all__'


class TableSerializer(serializers.ModelSerializer):

    label = serializers.CharField(source='__str__')

    class Meta:
        model = Table
        fields = '__all__'


class DatabaseSerializer(serializers.ModelSerializer):

    label = serializers.CharField(source='__str__')

    class Meta:
        model = Database
        fields = '__all__'


class NestedFunctionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Function
        fields = ('id', 'name')


class NestedColumnSerializer(serializers.ModelSerializer):

    class Meta:
        model = Column
        fields = ('id', 'name')


class NestedTableSerializer(serializers.ModelSerializer):

    columns = NestedColumnSerializer(many=True, read_only=True)

    class Meta:
        model = Table
        fields = ('id', 'name', 'columns')


class NestedDatabaseSerializer(serializers.ModelSerializer):

    tables = NestedTableSerializer(many=True, read_only=True)

    class Meta:
        model = Database
        fields = ('id', 'name', 'tables')


class MetaDBSerializer(serializers.ModelSerializer):

    tables = TableSerializer(many=True, read_only=True)

    class Meta:
        model = Database
        fields = (
            'name',
            'query_string',
            'description',
            'utype',
            'tables'
        )