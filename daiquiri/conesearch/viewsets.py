from django.utils.timezone import now
from django.http import HttpResponse

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, TokenAuthentication

from daiquiri.core.utils import get_client_ip
from daiquiri.stats.models import Record
from daiquiri.core.renderers import ErrorRenderer

from .adapter import ConeSearchAdapter
from .renderers import SearchRenderer
from .permissions import HasPermission


class SearchViewSet(viewsets.ViewSet):
    permission_classes = (HasPermission, )
    authentication_classes = (SessionAuthentication, TokenAuthentication)
    renderer_classes = (ErrorRenderer, )

    def list(self, request):
        adapter = ConeSearchAdapter()
        adapter.clean(request)

        if request.GET.get('download', True):
            # create a stats record for this cutout
            Record.objects.create(
                time=now(),
                resource_type='CONESEARCH',
                resource=adapter.sql_args,
                client_ip=get_client_ip(request),
                user=request.user if request.user.is_authenticated else None
            )

            # perform the cutout and send the file
            rows = adapter.fetch_rows()
            renderered_data = SearchRenderer().render(rows, renderer_context=self.get_renderer_context())
            return HttpResponse(renderered_data, content_type=SearchRenderer.media_type)
        else:
            # send an empty response
            return Response()
