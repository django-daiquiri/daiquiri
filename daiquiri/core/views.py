from django.conf import settings
from django.contrib.auth.mixins import (
    AccessMixin,
    PermissionRequiredMixin as DjangoPermissionRequiredMixin
)
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.shortcuts import render

from allauth.account.forms import LoginForm

from rules.contrib.views import PermissionRequiredMixin as RulesPermissionRequiredMixin


def home(request):
    if not request.user.is_authenticated():
        login_form = LoginForm()
        login_form.fields['login'].widget.attrs.pop("autofocus", None)
    else:
        login_form = None

    return render(request, 'core/home.html', {'form': login_form})


def bad_request(request):
    return render(request, 'core/400.html', status=400)


def forbidden(request):
    return render(request, 'core/403.html', status=403)


def not_found(request):
    return render(request, 'core/404.html', status=404)


def internal_server_error(request):
    return render(request, 'core/500.html', status=500)


class PermissionRedirectMixin(object):

    def handle_no_permission(self):
        if self.request.user.is_authenticated():
            raise PermissionDenied(self.get_permission_denied_message())

        return redirect_to_login(self.request.get_full_path(), self.get_login_url(), self.get_redirect_field_name())


class ModelPermissionMixin(PermissionRedirectMixin, DjangoPermissionRequiredMixin, object):
    pass


class ObjectPermissionMixin(PermissionRedirectMixin, RulesPermissionRequiredMixin, object):
    pass


class AnonymousAccessMixin(AccessMixin):
    anonymous_setting = None

    def dispatch(self, request, *args, **kwargs):
        if not getattr(settings, self.anonymous_setting) and not request.user.is_authenticated:
            return self.handle_no_permission()
        return super(AnonymousAccessMixin, self).dispatch(request, *args, **kwargs)
