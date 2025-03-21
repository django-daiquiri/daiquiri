from django.conf import settings
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404

from rest_framework import filters, mixins, viewsets
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend

from daiquiri.core.paginations import ListPagination
from daiquiri.core.permissions import HasModelPermission

from .models import Profile
from .permissions import GroupViewPermission, IsAuthManager
from .serializers import GroupSerializer, ProfileSerializer


class ProfileViewSet(mixins.UpdateModelMixin, mixins.ListModelMixin,
                     mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    permission_classes = (HasModelPermission, )
    authentication_classes = (SessionAuthentication, TokenAuthentication)

    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    pagination_class = ListPagination

    filter_backends = (filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend)
    ordering_fields = (
        'user__username',
        'user__email',
        'user__first_name',
        'user__last_name',
        'user__date_joined'
    )
    search_fields = (
        'user__username',
        'user__email',
        'user__first_name',
        'user__last_name'
    )
    filterset_fields = (
        'is_pending',
        'is_confirmed',
        'user__is_active',
        'user__is_staff',
        'user__is_superuser',
    )

    @action(detail=True, methods=['put'], permission_classes=[HasModelPermission])
    def confirm(self, request, pk=None):
        if not settings.AUTH_WORKFLOW:
            raise MethodNotAllowed('put')

        profile = get_object_or_404(Profile, pk=pk)
        profile.confirm(request)
        return Response(self.get_serializer(profile).data)

    @action(detail=True, methods=['put'], permission_classes=[HasModelPermission])
    def reject(self, request, pk=None):
        if not settings.AUTH_WORKFLOW:
            raise MethodNotAllowed('put')

        profile = get_object_or_404(Profile, pk=pk)
        profile.reject(request)
        return Response(self.get_serializer(profile).data)

    @action(detail=True, methods=['put'], permission_classes=[HasModelPermission])
    def activate(self, request, pk=None):
        if not settings.AUTH_WORKFLOW:
            raise MethodNotAllowed('put')

        profile = get_object_or_404(Profile, pk=pk)
        profile.activate(request)
        return Response(self.get_serializer(profile).data)

    @action(detail=True, methods=['put'], permission_classes=[HasModelPermission])
    def disable(self, request, pk=None):
        profile = get_object_or_404(Profile, pk=pk)
        profile.disable(request)
        return Response(self.get_serializer(profile).data)

    @action(detail=True, methods=['put'], permission_classes=[HasModelPermission])
    def enable(self, request, pk=None):
        profile = get_object_or_404(Profile, pk=pk)
        profile.enable(request)
        return Response(self.get_serializer(profile).data)


class SettingsViewSet(viewsets.GenericViewSet):
    permission_classes = (IsAuthManager, )
    authentication_classes = (SessionAuthentication, TokenAuthentication)

    queryset = {
        'AUTH_WORKFLOW': settings.AUTH_WORKFLOW,
        'AUTH_DETAIL_KEYS': settings.AUTH_DETAIL_KEYS
    }

    def list(self, request, *args, **kwargs):
        return Response(self.get_queryset())


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (GroupViewPermission, )
    authentication_classes = (SessionAuthentication, TokenAuthentication)

    queryset = Group.objects.order_by('name')
    serializer_class = GroupSerializer
