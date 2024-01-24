from django.db.models.expressions import fields
from rest_framework import serializers

from daiquiri.stats.models import Record


class RecordSerializer(serializers.ModelSerializer):


    class Meta:
        model = Record
        fields = '__all__'

