from django.conf import settings
from django.contrib.auth.mixins import AccessMixin
from django.views.generic import TemplateView

from daiquiri.core.views import ModelPermissionMixin


class QueryView(AccessMixin, TemplateView):
    template_name = 'query/query.html'

    def dispatch(self, request, *args, **kwargs):
        if not settings.QUERY['anonymous'] and not request.user.is_authenticated:
            return self.handle_no_permission()
        return super(QueryView, self).dispatch(request, *args, **kwargs)


class ExamplesView(ModelPermissionMixin, TemplateView):
    template_name = 'query/examples.html'
    permission_required = 'daiquiri_query.view_example'
