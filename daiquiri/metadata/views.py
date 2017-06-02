from django.views.generic import TemplateView

from daiquiri.core.views import ModelPermissionMixin

from .models import Database, Table


class ManagementView(ModelPermissionMixin, TemplateView):
    template_name = 'metadata/management.html'
    permission_required = 'daiquiri_metadata.view_database'


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
