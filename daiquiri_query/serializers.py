from rest_framework import serializers

from .models import QueryJob


class QueryJobSerializer(serializers.ModelSerializer):

    class Meta:
        model = QueryJob
