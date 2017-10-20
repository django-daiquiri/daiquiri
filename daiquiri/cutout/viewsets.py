from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication, TokenAuthentication

from .utils import get_adapter
from .permissions import HasPermission


class CutoutViewSet(viewsets.GenericViewSet):
    permission_classes = (HasPermission, )
    authentication_classes = (SessionAuthentication, TokenAuthentication)

    def list(self, request):
        adapter = get_adapter()
        adapter.clean(request)
        return adapter.perform_cutout(request)
