from django.conf import settings
from django.contrib.auth.mixins import AccessMixin
from django.views.generic import TemplateView

from .utils import get_adapter


class DatacubeView(AccessMixin, TemplateView):
    template_name = 'cutout/datacube.html'

    def dispatch(self, request, *args, **kwargs):
        if not settings.CUTOUT_ANONYMOUS and not request.user.is_authenticated:
            return self.handle_no_permission()
        return super(DatacubeView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(DatacubeView, self).get_context_data(**kwargs)
        context['defaults'] = get_adapter().defaults

        return context
