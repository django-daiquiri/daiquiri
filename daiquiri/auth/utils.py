from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from daiquiri.core.utils import send_mail


def get_account_workflow():
    if hasattr(settings, 'ACCOUNT_WORKFLOW') and settings.ACCOUNT_WORKFLOW in ['confirmation', 'activation']:
        return settings.ACCOUNT_WORKFLOW
    else:
        return None


def get_full_name(user):
    if user.first_name and user.last_name:
        return user.first_name + ' ' + user.last_name
    else:
        return user.username


def get_admin_emails():
    return [user.email for user in User.objects.filter(is_superuser=True)]


def send_request_confirmation(request, user):
    emails = get_admin_emails()
    context = {
        'user': user,
        'users_url': request.build_absolute_uri(reverse('users'))
    }
    send_mail(request, 'account/email/request_confirmation', context, emails)


def send_request_activation(request, user):
    emails = get_admin_emails()
    context = {
        'user': user,
        'users_url': request.build_absolute_uri(reverse('users'))
    }
    send_mail(request, 'account/email/request_activation', context, emails)


def send_notify_confirmation(request, user):
    emails = get_admin_emails()
    context = {
        'user': user,
        'request_user': request.user
    }
    send_mail(request, 'account/email/notify_confirmation', context, emails)


def send_notify_activation(request, user):
    emails = get_admin_emails()
    context = {
        'user': user,
        'request_user': request.user
    }
    send_mail(request, 'account/email/notify_activation', context, emails)


def send_activation(request, user):
    emails = get_admin_emails()
    context = {
        'user': user,
        'login_url': request.build_absolute_uri(reverse('account_login'))
    }
    send_mail(request, 'account/email/activation', context, emails)
