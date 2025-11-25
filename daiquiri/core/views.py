import hashlib

from django.conf import settings
from django.contrib.auth.mixins import AccessMixin
from django.contrib.auth.mixins import PermissionRequiredMixin as DjangoPermissionRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import View

from allauth.account.forms import LoginForm
from rules.contrib.views import PermissionRequiredMixin as RulesPermissionRequiredMixin

from daiquiri.core.utils import render_to_xml


def home(request):
    if not request.user.is_authenticated:
        login_form = LoginForm()
        login_form.fields['login'].widget.attrs.pop('autofocus', None)
    else:
        login_form = None

    return render(request, 'core/home.html', {'form': login_form})


def bad_request(request, exception):
    return render(request, 'core/400.html', status=400)


def forbidden(request, exception):
    return render(request, 'core/403.html', status=403)


def not_found(request, exception):
    return render(request, 'core/404.html', status=404)


def internal_server_error(request):
    return render(request, 'core/500.html', status=500)


class PermissionRedirectMixin:
    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            raise PermissionDenied(self.get_permission_denied_message())

        return redirect_to_login(
            self.request.get_full_path(), self.get_login_url(), self.get_redirect_field_name()
        )


class ModelPermissionMixin(PermissionRedirectMixin, DjangoPermissionRequiredMixin):
    pass


class ObjectPermissionMixin(PermissionRedirectMixin, RulesPermissionRequiredMixin):
    pass


class AnonymousAccessMixin(AccessMixin):
    anonymous_setting = None

    def dispatch(self, request, *args, **kwargs):
        if not getattr(settings, self.anonymous_setting) and not request.user.is_authenticated:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class SingleObjectXMLMixin(View):
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        context = self.get_context_data()
        renderer = self.renderer_class()

        return render_to_xml(request, renderer, context)

    def get_object(self):
        raise NotImplementedError()

    def get_context_data(self):
        raise NotImplementedError()


class CSRFViewMixin(View):
    @method_decorator(ensure_csrf_cookie)
    def get(self, request, *args, **kwargs):
        return super().get(self, request, *args, **kwargs)


class StoreIdViewMixin(View):
    def render_to_response(self, context, **response_kwargs):
        response = super().render_to_response(context, **response_kwargs)
        response.set_cookie('storeid', self.get_store_id(), samesite='Lax')
        return response

    def get_store_id(self):
        session_key = self.request.session.session_key or 'anonymous'
        return hashlib.sha256(session_key.encode()).hexdigest()
