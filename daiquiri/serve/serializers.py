from rest_framework import serializers

from daiquiri.metadata.models import Column


class ColumnSerializer(serializers.ModelSerializer):

    mode = serializers.SerializerMethodField()

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
            'arraysize',
            'principal',
            'indexed',
            'std',
            'mode'
        )

    def get_mode(self, obj):
        try:
            if 'meta.file' in obj['ucd']:
                return 'file'
            elif 'meta.note' in obj['ucd']:
                return 'note'
            elif 'meta.preview' in obj['ucd']:
                return 'preview'
            elif 'meta.ref' in obj['ucd']:
                return 'link'
        except (AttributeError, TypeError):
            pass

        return 'default'
