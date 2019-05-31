from django.views.generic import View

from daiquiri.metadata.models import Schema, Table

from .mixins import DataciteMixin
from .serializers import SchemaSerializer, TableSerializer
from .renderers import DataCiteRenderer


class SchemaView(DataciteMixin, View):

    renderer_class = DataCiteRenderer
    serializer_class = SchemaSerializer

    def get_object(self):
        schema_name = self.kwargs.get('schema_name')
        return Schema.objects.filter_by_metadata_access_level(self.request.user).get(name=schema_name)


class TableView(DataciteMixin, View):

    renderer_class = DataCiteRenderer
    serializer_class = TableSerializer

    def get_object(self):
        schema_name = self.kwargs.get('schema_name')
        table_name = self.kwargs.get('table_name')
        schema = Schema.objects.filter_by_metadata_access_level(self.request.user).get(name=schema_name)
        return Table.objects.filter_by_metadata_access_level(self.request.user).filter(schema=schema).get(name=table_name)
