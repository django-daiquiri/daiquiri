from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import ensure_csrf_cookie

from rest_framework import viewsets, mixins, filters
from rest_framework.decorators import detail_route
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.response import Response

from daiquiri_core.permissions import DaiquiriModelPermissions
from daiquiri_core.utils import get_referer_url_name

from .models import DetailKey, Profile
from .utils import get_account_workflow
from .serializers import ProfileSerializer
from .paginations import ProfilePagination
from .forms import UserForm, ProfileForm


@login_required()
def profile_update(request):
    next = get_referer_url_name(request, 'home')

    if request.method == 'POST':
        if 'cancel' in request.POST:
            next = request.POST.get('next')
            if next in ('profile_update', None):
                return HttpResponseRedirect(reverse('home'))
            else:
                return HttpResponseRedirect(reverse(next))

        user_form = UserForm(request.POST)
        profile_form = ProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            request.user.first_name = user_form.cleaned_data['first_name']
            request.user.last_name = user_form.cleaned_data['last_name']
            request.user.email = user_form.cleaned_data['email']
            request.user.save()

            # for detail_key in detail_keys:
            #     if not request.user.profile.details:
            #         request.user.profile.details = {}
            #     request.user.profile.details[detail_key.key] = profile_form.cleaned_data[detail_key.key]
            # request.user.profile.save()

            next = request.POST.get('next')
            if next in ('profile_update', None):
                return HttpResponseRedirect(reverse('home'))
            else:
                return HttpResponseRedirect(reverse(next))

    else:
        user_initial = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email
        }

        user_form = UserForm(initial=user_initial)
        profile_form = ProfileForm()

    return render(request, 'auth/profile_update_form.html', {'user_form': user_form, 'profile_form': profile_form, 'next': next})


@ensure_csrf_cookie
@permission_required('daiquiri_auth.view_profile')
def users(request):
    return render(request, 'auth/users.html', {
        'detail_keys': DetailKey.objects.all(),
        'account_workflow': get_account_workflow()
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
