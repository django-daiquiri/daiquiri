from django.contrib.auth.mixins import PermissionRequiredMixin as DjangoPermissionRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.shortcuts import render

from allauth.account.forms import LoginForm

from rules.contrib.views import PermissionRequiredMixin as RulesPermissionRequiredMixin


def home(request):
    if not request.user.is_authenticated():
        login_form = LoginForm()
    else:
        login_form = None

    return render(request, 'core/home.html', {'form': login_form})


class PermissionRedirectMixin(object):

    def handle_no_permission(self):
        if self.request.user.is_authenticated():
            raise PermissionDenied(self.get_permission_denied_message())

        return redirect_to_login(self.request.get_full_path(), self.get_login_url(), self.get_redirect_field_name())


class ModelPermissionMixin(PermissionRedirectMixin, DjangoPermissionRequiredMixin, object):
    pass


class ObjectPermissionMixin(PermissionRedirectMixin, RulesPermissionRequiredMixin, object):
    pass
