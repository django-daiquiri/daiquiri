from django.contrib.auth.mixins import AccessMixin
from django.views.generic import TemplateView

from daiquiri.core.views import CSRFViewMixin

from .permissions import HasPermission


class ArchiveView(AccessMixin, CSRFViewMixin, TemplateView):
    template_name = 'archive/archive.html'

    def dispatch(self, request, *args, **kwargs):

        if not HasPermission().has_permission(request):
            return self.handle_no_permission()
        return super(ArchiveView, self).dispatch(request, *args, **kwargs)
