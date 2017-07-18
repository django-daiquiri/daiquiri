from rest_framework import serializers

from daiquiri.query.validators import validate_table_name, validate_query_language


class SyncQueryJobCreateSerializer(serializers.Serializer):

    TABLE_NAME = serializers.CharField(required=False, validators=[validate_table_name])
    LANG = serializers.CharField(required=True, validators=[validate_query_language])
    QUERY = serializers.CharField(required=True)
