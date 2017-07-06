from django.views.generic import TemplateView

from daiquiri.core.views import ModelPermissionMixin
from daiquiri.core.utils import get_model_field_meta

from .models import Database, Table, Column, Function


class ManagementView(ModelPermissionMixin, TemplateView):
    template_name = 'metadata/management.html'
    permission_required = 'daiquiri_metadata.view_database'

    def get_context_data(self, **kwargs):
        context = super(ManagementView, self).get_context_data(**kwargs)
        context['meta'] = {
            'Database': get_model_field_meta(Database),
            'Table': get_model_field_meta(Table),
            'Column': get_model_field_meta(Column),
            'Function': get_model_field_meta(Function),
        }
        return context


class DatabaseView(TemplateView):
    template_name = 'metadata/database.html'

    def get_context_data(self, **kwargs):
        context = super(DatabaseView, self).get_context_data(**kwargs)
        context['database'] = Database.objects.get(name=self.kwargs.get('database_name'))
        return context


class TableView(TemplateView):
    template_name = 'metadata/table.html'

    def get_context_data(self, **kwargs):
        context = super(TableView, self).get_context_data(**kwargs)
        context['table'] = Table.objects.get(
            name=self.kwargs.get('table_name'),
            database__name=self.kwargs.get('database_name')
        )
        return context
