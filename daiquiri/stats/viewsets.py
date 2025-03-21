from rest_framework import filters, viewsets
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.pagination import PageNumberPagination

from django_filters.rest_framework import DjangoFilterBackend

from daiquiri.core.permissions import HasModelPermission
from daiquiri.stats.models import Record
from daiquiri.stats.serializers import RecordSerializer


class RecordViewSetPagination(PageNumberPagination):
    page_size = 1000
    page_size_query_param = 'page_size'
    max_page_size = 10000


class RecordViewSet(viewsets.ModelViewSet):
    permission_classes = (HasModelPermission, )
    authentication_classes = (SessionAuthentication, TokenAuthentication)
    http_method_names = ['get', ]

    queryset = Record.objects.all()
    serializer_class = RecordSerializer
    pagination_class = RecordViewSetPagination

    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    filterset_fields = ('user', 'resource_type', 'time')
    search_fields = ('user', 'resource_type', 'time')
    ordering_fields = ('time', 'resource_type')
