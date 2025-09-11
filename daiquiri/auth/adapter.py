import logging

from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse

from allauth.account.adapter import DefaultAccountAdapter
from allauth.core.exceptions import ImmediateHttpResponse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

logger = logging.getLogger(__name__)


class DaiquiriAccountAdapter(DefaultAccountAdapter):
    def is_safe_url(self, url):
        from django.utils.http import url_has_allowed_host_and_scheme

        return url_has_allowed_host_and_scheme(url, allowed_hosts=settings.ALLOWED_HOSTS)

    def save_user(self, request, user, form, commit=True):
        super().save_user(request, user, form)

        if settings.AUTH_WORKFLOW:
            user.save()
            user.profile.is_pending = True
            user.profile.save()

    def login(self, request, user):
        if settings.AUTH_WORKFLOW and user.profile.is_pending:
            raise ImmediateHttpResponse(HttpResponseRedirect(reverse('account_pending')))
        else:
            super().login(request, user)

    def is_open_for_signup(self, request):
        return settings.AUTH_SIGNUP


class DaiquiriSocialAccountAdapter(DefaultSocialAccountAdapter):
    def authentication_error(
        self, request, provider_id, error=None, exception=None, extra_context=None
    ):
        logger.error([provider_id, error, exception])
        super().authentication_error(request, provider_id, error, exception, extra_context)
