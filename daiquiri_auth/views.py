from django.shortcuts import render
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect

from .models import Profile, DetailKey
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

    return render(request, 'auth/login.html', {'form': form})


def logout(request):
    auth_logout(request)
    return HttpResponseRedirect('/')


@login_required()
def profile_update(request):
    next = request.META.get('HTTP_REFERER', None)
    detail_keys = DetailKey.objects.all()

    if request.method == 'POST':
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

            return HttpResponseRedirect('/')

    else:
        user_initial = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email
        }

        user_form = UserForm(initial=user_initial)
        profile_form = ProfileForm(profile=request.user.profile, detail_keys=detail_keys)

    return render(request, 'auth/profile_update_form.html', {'user_form': user_form, 'profile_form': profile_form, 'next': next})
