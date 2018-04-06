from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from daiquiri.core.views import ModelPermissionMixin, AnonymousAccessMixin
from daiquiri.core.utils import get_model_field_meta

from .models import QueryJob, Example


class QueryView(AnonymousAccessMixin, TemplateView):
    template_name = 'query/query.html'
    anonymous_setting = 'QUERY_ANONYMOUS'


class JobsView(LoginRequiredMixin, TemplateView):
    template_name = 'query/jobs.html'

    def get_context_data(self, **kwargs):
        context = super(JobsView, self).get_context_data(**kwargs)
        context['phases'] = QueryJob.PHASE_CHOICES
        return context


class ExamplesView(ModelPermissionMixin, TemplateView):

    template_name = 'query/examples.html'
    permission_required = 'daiquiri_query.view_example'

    def get_context_data(self, **kwargs):
        context = super(ExamplesView, self).get_context_data(**kwargs)
        context['meta'] = {
            'Example': get_model_field_meta(Example)
        }
        return context
