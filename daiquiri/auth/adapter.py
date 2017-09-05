import logging

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.exceptions import ImmediateHttpResponse

logger = logging.getLogger(__name__)


class DaiquiriAccountAdapter(DefaultAccountAdapter):

    def is_safe_url(self, url):
        from django.utils.http import is_safe_url
        return is_safe_url(url, allowed_hosts=settings.ALLOWED_HOSTS)

    def save_user(self, request, user, form, commit=True):
        super(DaiquiriAccountAdapter, self).save_user(request, user, form)

        if settings.AUTH_WORKFLOW:
            user.save()
            user.profile.is_pending = True
            user.profile.save()

    def login(self, request, user):
        if settings.AUTH_WORKFLOW and user.profile.is_pending:
            raise ImmediateHttpResponse(HttpResponseRedirect(reverse('account_pending')))
        else:
            super(DaiquiriAccountAdapter, self).login(request, user)


class DaiquiriSocialAccountAdapter(DefaultSocialAccountAdapter):

    def authentication_error(self, request, provider_id, error=None, exception=None, extra_context=None):
        logger.error([provider_id, error, exception])
        super(DaiquiriSocialAccountAdapter, self).authentication_error(request, provider_id, error, exception, extra_context)
