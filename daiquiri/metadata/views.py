from django.http import Http404
from django.views.generic import TemplateView

from daiquiri.core.views import ModelPermissionMixin
from daiquiri.core.utils import get_model_field_meta

from .models import Schema, Table, Column, Function


class ManagementView(ModelPermissionMixin, TemplateView):
    template_name = 'metadata/management.html'
    permission_required = 'daiquiri_metadata.view_schema'

    def get_context_data(self, **kwargs):
        context = super(ManagementView, self).get_context_data(**kwargs)
        context['meta'] = {
            'Schema': get_model_field_meta(Schema),
            'Table': get_model_field_meta(Table),
            'Column': get_model_field_meta(Column),
            'Function': get_model_field_meta(Function),
        }
        return context


class SchemaView(TemplateView):
    template_name = 'metadata/schema.html'

    def get_context_data(self, **kwargs):
        context = super(SchemaView, self).get_context_data(**kwargs)

        schema_name = self.kwargs.get('schema_name')

        try:
            schema = Schema.objects.filter_by_metadata_access_level(self.request.user).get(name=schema_name)
        except Schema.DoesNotExist:
            raise Http404()

        context['schema'] = schema
        context['tables'] = schema.tables.filter_by_metadata_access_level(self.request.user)
        return context


class TableView(TemplateView):
    template_name = 'metadata/table.html'

    def get_context_data(self, **kwargs):
        context = super(TableView, self).get_context_data(**kwargs)

        schema_name = self.kwargs.get('schema_name')
        table_name = self.kwargs.get('table_name')

        try:
            schema = Schema.objects.filter_by_metadata_access_level(self.request.user).get(name=schema_name)
        except Schema.DoesNotExist:
            raise Http404()

        try:
            table = Table.objects.filter_by_metadata_access_level(self.request.user).filter(schema=schema).get(name=table_name)
        except Table.DoesNotExist:
            raise Http404()

        context['schema'] = schema
        context['table'] = table
        context['columns'] = table.columns.filter_by_metadata_access_level(self.request.user)
        return context
