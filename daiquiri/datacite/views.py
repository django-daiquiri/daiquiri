from django.views.generic import View

from daiquiri.metadata.models import Schema

from .mixins import DataciteMixin
from .serializers import SchemaSerializer
from .renderers import DataCiteRenderer


class SchemaView(DataciteMixin, View):

    renderer_class = DataCiteRenderer
    serializer_class = SchemaSerializer

    def get_object(self):
        schema_name = self.kwargs.get('schema_name')
        return Schema.objects.filter_by_metadata_access_level(self.request.user).get(name=schema_name)
