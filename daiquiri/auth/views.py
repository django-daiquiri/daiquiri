from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from rest_framework.authtoken.models import Token

from allauth.account.views import PasswordChangeView as AllauthPasswordChangeView
from allauth.account.views import PasswordSetView as AllauthPasswordSetView
from allauth.account.views import logout as allauth_logout

from daiquiri.auth.models import Profile
from daiquiri.core.utils import get_next, get_referer_path_info
from daiquiri.core.views import CSRFViewMixin, ModelPermissionMixin, StoreIdViewMixin

from .forms import ProfileForm, UserForm


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


def terms_of_use(request):
    context = {}
    if not settings.AUTH_TERMS_OF_USE:
        raise Http404

    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        if request.method == 'POST':
            if 'consent' in request.POST:
                profile.consent = True
                profile.save()
        context["consent"] = profile.consent

    return render(request, 'account/terms_of_use_page.html', context)


@login_required()
def profile_json(request):
    return JsonResponse({
        'username': request.user.username
    })


@login_required()
def token(request):
    if request.method == 'POST':
        try:
            Token.objects.get(user=request.user).delete()
        except Token.DoesNotExist:
            pass

    token, created = Token.objects.get_or_create(user=request.user)
    return render(request, 'account/account_token.html', {
        'token': token
    })


def logout(request, *args, **kwargs):
    response = allauth_logout(request, *args, **kwargs)

    return response


class UsersView(ModelPermissionMixin, CSRFViewMixin, StoreIdViewMixin, TemplateView):
    template_name = 'auth/users.html'
    permission_required = 'daiquiri_auth.view_profile'


class PasswordChangeView(AllauthPasswordChangeView):

    success_url = reverse_lazy('account_change_password_done')


password_change = login_required(PasswordChangeView.as_view())


class PasswordSetView(AllauthPasswordSetView):

    success_url = reverse_lazy('account_set_password_done')


password_set = login_required(PasswordSetView.as_view())
