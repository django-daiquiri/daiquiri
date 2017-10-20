from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.decorators import list_route

from .utils import get_adapter
from .permissions import HasPermission


class CutoutViewSet(viewsets.GenericViewSet):
    permission_classes = (HasPermission, )
    authentication_classes = (SessionAuthentication, TokenAuthentication)

    def list(self, request):
        adapter = get_adapter()
        adapter.clean(request)
        return adapter.perform_cutout(request)

    @list_route(methods=['get'])
    def validate(self, request):
        adapter = get_adapter()
        adapter.clean(request)
        return Response()
