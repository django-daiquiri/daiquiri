from rest_framework import serializers


class JSONField(serializers.JSONField):

    def to_internal_value(self, data):
        if not isinstance(data, dict):
            self.fail('invalid')

        return super(JSONField, self).to_internal_value(data)


class ChoicesSerializer(serializers.Serializer):
    id = serializers.SerializerMethodField()
    text = serializers.SerializerMethodField()

    def get_id(self, obj):
        return obj[0]

    def get_text(self, obj):
        return obj[1]
