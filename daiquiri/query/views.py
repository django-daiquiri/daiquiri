from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from daiquiri.core.utils import get_model_field_meta
from daiquiri.core.views import AnonymousAccessMixin, CSRFViewMixin, ModelPermissionMixin, StoreIdViewMixin

from .models import Example, QueryJob


class QueryView(AnonymousAccessMixin, CSRFViewMixin, StoreIdViewMixin, TemplateView):
    template_name = 'query/query.html'
    anonymous_setting = 'QUERY_ANONYMOUS'


class JobsView(LoginRequiredMixin, CSRFViewMixin, TemplateView):
    template_name = 'query/jobs.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['phases'] = QueryJob.PHASE_CHOICES
        return context


class ExamplesView(ModelPermissionMixin, CSRFViewMixin, TemplateView):

    template_name = 'query/examples.html'
    permission_required = 'daiquiri_query.view_example'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['meta'] = {
            'Example': get_model_field_meta(Example)
        }
        return context


class NewJobsView(LoginRequiredMixin, CSRFViewMixin, StoreIdViewMixin, TemplateView):
    template_name = 'query/new/jobs.html'


class NewExamplesView(ModelPermissionMixin, CSRFViewMixin, StoreIdViewMixin, TemplateView):

    template_name = 'query/new/examples.html'
    permission_required = 'daiquiri_query.view_example'
