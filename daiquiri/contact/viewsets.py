from rest_framework import filters, viewsets
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from django_filters.rest_framework import DjangoFilterBackend

from daiquiri.core.paginations import ListPagination
from daiquiri.core.permissions import HasModelPermission
from daiquiri.core.viewsets import ChoicesViewSet

from .filters import SpamBackend
from .models import ContactMessage
from .serializers import ContactMessageSerializer


class ContactMessageViewSet(viewsets.ModelViewSet):
    permission_classes = (HasModelPermission, )
    authentication_classes = (SessionAuthentication, TokenAuthentication)

    queryset = ContactMessage.objects.all()

    serializer_class = ContactMessageSerializer
    pagination_class = ListPagination

    filter_backends = (
        filters.SearchFilter,
        filters.OrderingFilter,
        DjangoFilterBackend,
        SpamBackend
    )
    search_fields = ('author', 'email', 'subject', 'message', 'status')
    filterset_fields = ('status', )


class StatusViewSet(ChoicesViewSet):
    permission_classes = (IsAuthenticated, )
    queryset = ContactMessage.STATUS_CHOICES
