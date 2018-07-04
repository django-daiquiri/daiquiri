from django.conf import settings
from django.utils.timezone import now

from rest_framework import viewsets, mixins, filters
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from daiquiri.core.permissions import HasModelPermission
from daiquiri.core.paginations import ListPagination
from daiquiri.core.viewsets import ChoicesViewSet

from .models import Meeting, Participant, Contribution
from .serializers import MeetingSerializer, ParticipantSerializer, ContributionSerializer
from .filters import ParticipantFilterBackend

class MeetingViewSet(mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.UpdateModelMixin,
                     viewsets.GenericViewSet):

    permission_classes = (HasModelPermission, )
    authentication_classes = (SessionAuthentication, TokenAuthentication)

    queryset = Meeting.objects.all()
    serializer_class = MeetingSerializer


class ParticipantViewSet(mixins.ListModelMixin,
                         mixins.RetrieveModelMixin,
                         mixins.CreateModelMixin,
                         mixins.UpdateModelMixin,
                         viewsets.GenericViewSet):

    permission_classes = (HasModelPermission, )
    authentication_classes = (SessionAuthentication, TokenAuthentication)

    queryset = Participant.objects.all()
    serializer_class = ParticipantSerializer
    pagination_class = ListPagination

    filter_backends = (filters.SearchFilter, filters.OrderingFilter, ParticipantFilterBackend)
    ordering_fields = ('last_name', 'email')
    search_fields = ('first_name', 'last_name', 'email')

    def create(self, request, *args, **kwargs):
        request.data['registered'] = now()
        return super(ParticipantViewSet, self).create(request, *args, **kwargs)


class ContributionViewSet(mixins.ListModelMixin,
                          mixins.RetrieveModelMixin,
                          mixins.CreateModelMixin,
                          mixins.UpdateModelMixin,
                          viewsets.GenericViewSet):

    permission_classes = (HasModelPermission, )
    authentication_classes = (SessionAuthentication, TokenAuthentication)

    queryset = Contribution.objects.all()
    serializer_class = ContributionSerializer
    pagination_class = ListPagination

    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    ordering_fields = ()
    search_fields = ()


class ContributionTypeViewSet(ChoicesViewSet):
    permission_classes = (IsAuthenticated, )
    authentication_classes = (SessionAuthentication, TokenAuthentication)

    queryset = settings.MEETINGS_CONTRIBUTION_TYPES


class StatusViewSet(ChoicesViewSet):
    permission_classes = (IsAuthenticated, )
    authentication_classes = (SessionAuthentication, TokenAuthentication)

    queryset = Participant.STATUS_CHOICES


class PaymentViewSet(ChoicesViewSet):
    permission_classes = (IsAuthenticated, )
    authentication_classes = (SessionAuthentication, TokenAuthentication)

    queryset = Participant.PAYMENT_CHOICES
