import json
from uuid import UUID


class UUIDJSONEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, UUID):
            return obj.hex

        return json.JSONEncoder.default(self, obj)
