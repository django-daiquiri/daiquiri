from django.utils.timezone import now

from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from daiquiri.core.utils import get_client_ip
from daiquiri.stats.models import Record

from .adapter import CutOutAdapter
from .permissions import HasPermission
from .renderers import CutOutErrorRenderer


class CutOutViewSet(APIView):

    permission_classes = (HasPermission, )
    authentication_classes = (SessionAuthentication, TokenAuthentication)
    renderer_classes = (CutOutErrorRenderer, JSONRenderer)

    def get(self, request, resource=None):

        adapter = CutOutAdapter()
        adapter.clean(request, resource)

        if request.GET.get('download', True):
            # create a stats record for this cutout
            Record.objects.create(
                time=now(),
                resource_type='CUTOUT',
                resource=adapter.args,
                client_ip=get_client_ip(request),
                user=request.user if request.user.is_authenticated else None
            )

            # stream the table
            return adapter.stream()
        else:
            # send an empty response
            return Response()
