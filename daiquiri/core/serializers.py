from rest_framework import serializers

from .utils import make_query_dict_upper_case


class JSONDictField(serializers.JSONField):

    initial = dict

    def to_internal_value(self, data):
        data = super().to_internal_value(data)

        if not isinstance(data, dict):
            self.fail('invalid')

        return data


class JSONListField(serializers.JSONField):

    initial = list

    def to_internal_value(self, data):
        data = super().to_internal_value(data)

        if not isinstance(data, list):
            self.fail('invalid')

        return data


class ChoicesSerializer(serializers.Serializer):
    id = serializers.SerializerMethodField()
    text = serializers.SerializerMethodField()

    def get_id(self, obj):
        return obj[0]

    def get_text(self, obj):
        return obj[1]


class CaseInsensitiveSerializer(serializers.Serializer):

    def __init__(self, *args, **kwargs):
        # make all the keys in kwargs['data'] upper case
        if 'data' in kwargs:
            kwargs['data'] = make_query_dict_upper_case(kwargs['data'])

        super().__init__(*args, **kwargs)
