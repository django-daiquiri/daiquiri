from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated

from daiquiri.core.viewsets import ChoicesViewSet
from daiquiri.core.permissions import DaiquiriModelPermissions

from .models import ContactMessage
from .serializers import ContactMessageSerializer
from .paginations import MessagePagination


class ContactMessageViewSet(viewsets.ModelViewSet):
    permission_classes = (DaiquiriModelPermissions, )

    queryset = ContactMessage.objects.all()

    serializer_class = ContactMessageSerializer
    pagination_class = MessagePagination

    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    search_fields = ('author', 'email', 'subject', 'status')


class StatusViewSet(ChoicesViewSet):
    permission_classes = (IsAuthenticated, )
    queryset = ContactMessage.STATUS_CHOICES
