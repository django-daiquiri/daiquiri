from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, TokenAuthentication

from daiquiri.core.viewsets import ChoicesViewSet
from daiquiri.core.permissions import HasModelPermission
from daiquiri.core.paginations import ListPagination

from .models import ContactMessage
from .serializers import ContactMessageSerializer
from .filters import SpamBackend


class ContactMessageViewSet(viewsets.ModelViewSet):
    permission_classes = (HasModelPermission, )
    authentication_classes = (SessionAuthentication, TokenAuthentication)

    queryset = ContactMessage.objects.all()

    serializer_class = ContactMessageSerializer
    pagination_class = ListPagination

    filter_backends = (
        filters.SearchFilter,
        filters.OrderingFilter,
        filters.DjangoFilterBackend,
        SpamBackend
    )
    search_fields = ('author', 'email', 'subject', 'message', 'status')
    filter_fields = ('status', )


class StatusViewSet(ChoicesViewSet):
    permission_classes = (IsAuthenticated, )
    queryset = ContactMessage.STATUS_CHOICES
