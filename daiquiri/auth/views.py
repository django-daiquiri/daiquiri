import json

from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from daiquiri.core.utils import get_referer_path_info, get_next
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

from .utils import get_account_workflow
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
