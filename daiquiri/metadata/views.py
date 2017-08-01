from django.http import Http404
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

        database_name = self.kwargs.get('database_name')

        try:
            database = Database.objects.filter_by_metadata_access_level(self.request.user).get(name=database_name)
        except Database.DoesNotExist:
            raise Http404()

        context['database'] = database
        context['tables'] = database.tables.filter_by_metadata_access_level(self.request.user)
        return context


class TableView(TemplateView):
    template_name = 'metadata/table.html'

    def get_context_data(self, **kwargs):
        context = super(TableView, self).get_context_data(**kwargs)

        database_name = self.kwargs.get('database_name')
        table_name = self.kwargs.get('table_name')

        try:
            database = Database.objects.filter_by_metadata_access_level(self.request.user).get(name=database_name)
        except Database.DoesNotExist:
            raise Http404()

        try:
            table = Table.objects.filter_by_metadata_access_level(self.request.user).filter(database=database).get(name=table_name)
        except Table.DoesNotExist:
            raise Http404()

        context['database'] = database
        context['table'] = table
        context['columns'] = table.columns.filter_by_metadata_access_level(self.request.user)
        return context
