import json

from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import ensure_csrf_cookie

from rest_framework import viewsets, mixins, filters
from rest_framework.decorators import detail_route
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.response import Response

from daiquiri.core.permissions import DaiquiriModelPermissions
from daiquiri.core.utils import get_referer_path_info, get_next

from .models import Profile
from .utils import get_account_workflow
from .serializers import ProfileSerializer
from .paginations import ProfilePagination
from .forms import UserForm, ProfileForm


@login_required()
def profile_update(request):
    user_form = UserForm(request.POST or None, instance=request.user)
    profile_form = ProfileForm(request.POST or None, instance=request.user.profile)

    if request.method == 'POST':
        if 'cancel' in request.POST:
            return HttpResponseRedirect(get_next(request))

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return HttpResponseRedirect(get_next(request))

    return render(request, 'account/account_profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'next': get_referer_path_info(request, default='/')
    })


@ensure_csrf_cookie
@permission_required('daiquiri_auth.view_profile')
def users(request):
    # get urls to the admin interface to be used with angular
    user_admin_url = reverse('admin:auth_user_change', args=['row.id']).replace('row.id', '{$ row.id $}')
    profile_admin_url = reverse('admin:daiquiri_auth_profile_change', args=['row.id']).replace('row.id', '{$ row.id $}')

    detail_keys = settings.AUTH['detail_keys']
    for detail_key in detail_keys:
        detail_key['options_json'] = json.dumps(detail_key['options'])
        detail_key['model'] = 'service.current_row.details.%s' % detail_key['key']
        detail_key['errors'] = 'service.errors.%s' % detail_key['key']

    return render(request, 'auth/users.html', {
        'detail_keys': detail_keys,
        'account_workflow': get_account_workflow(),
        'user_admin_url': user_admin_url,
        'profile_admin_url': profile_admin_url
    })


class ProfileViewSet(mixins.UpdateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    permission_classes = (DaiquiriModelPermissions, )

    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    pagination_class = ProfilePagination

    filter_backends = (filters.SearchFilter, filters.OrderingFilter)
    ordering_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')

    @detail_route(methods=['put'], permission_classes=[DaiquiriModelPermissions])
    def confirm(self, request, pk=None):
        if not get_account_workflow():
            raise MethodNotAllowed()

        profile = get_object_or_404(Profile, pk=pk)
        profile.confirm(request)
        return Response(self.get_serializer(profile).data)

    @detail_route(methods=['put'], permission_classes=[DaiquiriModelPermissions])
    def activate(self, request, pk=None):
        if not get_account_workflow():
            raise MethodNotAllowed()

        profile = get_object_or_404(Profile, pk=pk)
        profile.activate(request)
        return Response(self.get_serializer(profile).data)

    @detail_route(methods=['put'], permission_classes=[DaiquiriModelPermissions])
    def disable(self, request, pk=None):
        profile = get_object_or_404(Profile, pk=pk)
        profile.disable(request)
        return Response(self.get_serializer(profile).data)

    @detail_route(methods=['put'], permission_classes=[DaiquiriModelPermissions])
    def enable(self, request, pk=None):
        profile = get_object_or_404(Profile, pk=pk)
        profile.enable(request)
        return Response(self.get_serializer(profile).data)
