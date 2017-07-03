from django.contrib.auth.models import Group

from rest_framework import serializers

from ..models import Database, Table, Column, Function


class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = ('id', 'name')


class FunctionSerializer(serializers.ModelSerializer):

    label = serializers.CharField(source='__str__', read_only=True)

    class Meta:
        model = Function
        fields = '__all__'


class ColumnSerializer(serializers.ModelSerializer):

    label = serializers.CharField(source='__str__', read_only=True)

    class Meta:
        model = Column
        fields = '__all__'


class TableSerializer(serializers.ModelSerializer):

    label = serializers.CharField(source='__str__', read_only=True)

    class Meta:
        model = Table
        fields = '__all__'


class DatabaseSerializer(serializers.ModelSerializer):

    label = serializers.CharField(source='__str__', read_only=True)

    class Meta:
        model = Database
        fields = '__all__'
