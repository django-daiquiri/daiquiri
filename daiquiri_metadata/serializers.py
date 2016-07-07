from django.contrib.auth.models import Group

from rest_framework import serializers

from .models import Database, Table, Column, Function


class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = ('id', 'name')


class DatabaseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Database
        fields = '__all__'


class TableSerializer(serializers.ModelSerializer):

    class Meta:
        model = Table
        fields = '__all__'


class ColumnSerializer(serializers.ModelSerializer):

    class Meta:
        model = Column
        fields = '__all__'


class FunctionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Function
        fields = '__all__'


class NestedFunctionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Function
        fields = ('id', '__str__', 'name')


class NestedColumnSerializer(serializers.ModelSerializer):

    class Meta:
        model = Column
        fields = ('id', '__str__', 'name')


class NestedTableSerializer(serializers.ModelSerializer):

    columns = NestedColumnSerializer(many=True, read_only=True)

    class Meta:
        model = Table
        fields = ('id', '__str__', 'name', 'columns')


class NestedDatabaseSerializer(serializers.ModelSerializer):

    tables = NestedTableSerializer(many=True, read_only=True)

    class Meta:
        model = Database
        fields = ('id', '__str__', 'name', 'tables')
