from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from allauth.account.adapter import DefaultAccountAdapter
from allauth.exceptions import ImmediateHttpResponse


class DaiquiriAccountAdapter(DefaultAccountAdapter):

    WORKFLOWS = ('confirmation', 'activation')

    def is_safe_url(self, url):
        from django.utils.http import is_safe_url
        return is_safe_url(url, allowed_hosts=settings.ALLOWED_HOSTS)

    def has_workflow(self):
        return hasattr(settings, 'ACCOUNT_WORKFLOW') and settings.ACCOUNT_WORKFLOW in self.WORKFLOWS

    def save_user(self, request, user, form, commit=True):
        super(DaiquiriAccountAdapter, self).save_user(request, user, form)

        if self.has_workflow():
            user.save()
            user.profile.is_pending = True
            user.profile.save()

    def login(self, request, user):
        if self.has_workflow() and user.profile.is_pending:
            raise ImmediateHttpResponse(HttpResponseRedirect(reverse('account_pending')))
        else:
            super(DaiquiriAccountAdapter, self).login(request, user)
