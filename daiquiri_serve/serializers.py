from rest_framework import serializers

from daiquiri_metadata.models import Column


class ColumnSerializer(serializers.ModelSerializer):

    class Meta:
        model = Column
        fields = (
            'id',
            'order',
            'name',
            'description',
            'unit',
            'ucd',
            'datatype',
            'size',
            'principal',
            'indexed',
            'std'
        )
