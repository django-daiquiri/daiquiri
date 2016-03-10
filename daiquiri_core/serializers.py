from rest_framework.serializers import JSONField as DefaultJSONField


class JSONField(DefaultJSONField):

    def to_internal_value(self, data):
        if not isinstance(data, dict):
            self.fail('invalid')

        return super(JSONField, self).to_internal_value(data)
