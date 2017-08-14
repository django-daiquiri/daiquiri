from django.conf import settings
from django.contrib.auth.mixins import AccessMixin
from django.views.generic import TemplateView

from daiquiri.core.views import ModelPermissionMixin
from daiquiri.core.utils import get_model_field_meta

from .models import Example


class QueryView(AccessMixin, TemplateView):
    template_name = 'query/query.html'

    def dispatch(self, request, *args, **kwargs):
        if not settings.QUERY_ANONYMOUS and not request.user.is_authenticated:
            return self.handle_no_permission()
        return super(QueryView, self).dispatch(request, *args, **kwargs)


class ExamplesView(ModelPermissionMixin, TemplateView):

    template_name = 'query/examples.html'
    permission_required = 'daiquiri_query.view_example'

    def get_context_data(self, **kwargs):
        context = super(ExamplesView, self).get_context_data(**kwargs)
        context['meta'] = {
            'Example': get_model_field_meta(Example)
        }
        return context
