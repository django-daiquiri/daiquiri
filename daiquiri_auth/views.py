from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.translation import ugettext_lazy as _


from rest_framework import viewsets, mixins

from daiquiri_core.utils import get_referer_url_name

from .models import DetailKey
from .serializers import UserSerializer
from .paginations import UserPagination
from .forms import LoginForm, UserForm, ProfileForm


def login(request):
    form = LoginForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(username=username, password=password)

            if user:
                auth_login(request, user)
                if request.POST.get('next'):
                    return HttpResponseRedirect(request.POST.get('next'))
                else:
                    return HttpResponseRedirect('/')
            else:
                return render(request, 'auth/login_form.html', {'form': form, 'message': _("Your login was not successful. Your username and password didn't match. Please try again.")})

    return render(request, 'auth/login_form.html', {'form': form})


def logout(request):
    auth_logout(request)
    return HttpResponseRedirect('/')


@login_required()
def profile_update(request):
    next = get_referer_url_name(request, 'home')
    detail_keys = DetailKey.objects.all()

    if request.method == 'POST':
        if 'cancel' in request.POST:
            next = request.POST.get('next')
            if next == 'profile_update':
                return HttpResponseRedirect(reverse('home'))
            else:
                return HttpResponseRedirect(reverse(next))

        user_form = UserForm(request.POST)
        profile_form = ProfileForm(request.POST, profile=request.user.profile, detail_keys=detail_keys)

        if user_form.is_valid() and profile_form.is_valid():
            request.user.first_name = user_form.cleaned_data['first_name']
            request.user.last_name = user_form.cleaned_data['last_name']
            request.user.email = user_form.cleaned_data['email']
            request.user.save()

            for detail_key in detail_keys:
                if not request.user.profile.details:
                    request.user.profile.details = {}
                request.user.profile.details[detail_key.key] = profile_form.cleaned_data[detail_key.key]
            request.user.profile.save()

            next = request.POST.get('next')
            if next == 'profile_update':
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
        profile_form = ProfileForm(profile=request.user.profile, detail_keys=detail_keys)

    return render(request, 'auth/profile_update_form.html', {'user_form': user_form, 'profile_form': profile_form, 'next': next})


@ensure_csrf_cookie
def users(request):
    return render(request, 'auth/users.html', {})


class UserViewSet(mixins.UpdateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = UserPagination
