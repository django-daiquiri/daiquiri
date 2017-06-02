from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from daiquiri.core.views import ModelPermissionMixin


class QueryView(LoginRequiredMixin, TemplateView):
    template_name = 'query/query.html'


class ExamplesView(ModelPermissionMixin, TemplateView):
    template_name = 'query/examples.html'
    permission_required = 'daiquiri_query.view_example'
