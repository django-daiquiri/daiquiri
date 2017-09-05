import json

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from daiquiri.core.utils import get_referer_path_info, get_next
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render

from rest_framework.authtoken.models import Token

from allauth.account.views import logout as allauth_logout

from daiquiri.core.views import ModelPermissionMixin

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

    # delete wordpress cookies
    for cookie in request.COOKIES:
        if cookie.startswith('wordpress') or cookie.startswith('wp-settings'):
            response.delete_cookie(cookie)

    return response


class UsersView(ModelPermissionMixin, TemplateView):
    template_name = 'auth/users.html'
    permission_required = 'daiquiri_auth.view_profile'

    def get_context_data(self, **kwargs):
        # get urls to the admin interface to be used with angular
        user_admin_url = reverse('admin:auth_user_change', args=['row.id']).replace('row.id', '{$ row.id $}')
        profile_admin_url = reverse('admin:daiquiri_auth_profile_change', args=['row.id']).replace('row.id', '{$ row.id $}')

        detail_keys = settings.AUTH_DETAIL_KEYS
        for detail_key in detail_keys:
            detail_key['options_json'] = json.dumps(detail_key['options'])
            detail_key['model'] = 'service.current_row.details.%s' % detail_key['key']
            detail_key['errors'] = 'service.errors.%s' % detail_key['key']

        context = super(UsersView, self).get_context_data(**kwargs)
        context.update({
            'detail_keys': detail_keys,
            'user_admin_url': user_admin_url,
            'profile_admin_url': profile_admin_url
        })
        return context
