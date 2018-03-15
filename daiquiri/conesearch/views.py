from django.conf import settings
from django.contrib.auth.mixins import AccessMixin
from django.http import HttpResponse
from django.views.generic import View
from django.utils.timezone import now

from daiquiri.core.utils import get_client_ip
from daiquiri.stats.models import Record

from .adapter import ConeSearchAdapter
from .renderers import ConeSearchErrorRenderer


class ConeSearchView(AccessMixin, View):

    def dispatch(self, request, *args, **kwargs):
        if not settings.CONESEARCH_ANONYMOUS and not request.user.is_authenticated:
            return self.handle_no_permission()
        return super(ConeSearchView, self).dispatch(request, *args, **kwargs)

    def get(self, request, resource=None):

        adapter = ConeSearchAdapter()
        errors = adapter.clean(request, resource)

        if errors:
            renderered_data = ConeSearchErrorRenderer().render(errors)
            return HttpResponse(renderered_data, content_type=ConeSearchErrorRenderer.media_type)
        else:
            if request.GET.get('download', True):
                # create a stats record for this cutout
                Record.objects.create(
                    time=now(),
                    resource_type='CONESEARCH',
                    resource=adapter.args,
                    client_ip=get_client_ip(request),
                    user=request.user if request.user.is_authenticated else None
                )

                # stream the table
                return adapter.stream()
            else:
                # send an empty response
                return HttpResponse()
