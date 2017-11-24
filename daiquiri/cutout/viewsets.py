from django.utils.timezone import now

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, TokenAuthentication

from daiquiri.core.utils import get_client_ip
from daiquiri.stats.models import Record

from .utils import get_adapter
from .permissions import HasPermission


class DatacubeViewSet(viewsets.GenericViewSet):
    permission_classes = (HasPermission, )
    authentication_classes = (SessionAuthentication, TokenAuthentication)

    def list(self, request):
        adapter = get_adapter()
        adapter.clean(request)

        if request.GET.get('download', True):
            # create a stats record for this job
            Record.objects.create(
                time=now(),
                resource_type='CUTOUT',
                resource=adapter.__dict__,
                client_ip=get_client_ip(request),
                user=request.user
            )

            return adapter.perform_cutout(request)
        else:
            return Response()
