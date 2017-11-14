from django.utils.timezone import now

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.decorators import list_route

from daiquiri.core.utils import get_client_ip
from daiquiri.stats.models import Record

from .utils import get_adapter
from .permissions import HasPermission


class CutoutViewSet(viewsets.GenericViewSet):
    permission_classes = (HasPermission, )
    authentication_classes = (SessionAuthentication, TokenAuthentication)

    def list(self, request):
        adapter = get_adapter()
        adapter.clean(request)

        # create a stats record for this job
        Record.objects.create(
            time=now(),
            resource_type='CUTOUT',
            resource=adapter.__dict__,
            client_ip=get_client_ip(request),
            user=request.user
        )

        return adapter.perform_cutout(request)

    @list_route(methods=['get'])
    def validate(self, request):
        adapter = get_adapter()
        adapter.clean(request)
        return Response()
