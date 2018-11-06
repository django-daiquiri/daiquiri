from django.urls import reverse
from django.contrib.auth.models import User, Permission
from django.db.models import Q

from daiquiri.core.utils import send_mail, get_admin_emails


def get_full_name(user):
    if user.first_name and user.last_name:
        return user.first_name + ' ' + user.last_name
    else:
        return user.username


def get_manager_emails():
    permissions = Permission.objects.filter(content_type__app_label='daiquiri_auth', codename='view_profile')
    users = User.objects.filter(Q(groups__permissions__in=permissions) | Q(user_permissions__in=permissions)).distinct()
    return [user.email for user in users] + get_admin_emails()


def send_request_confirmation(request, user):
    '''
    Sends an email to the admins once a users email was validated.
    '''
    emails = get_manager_emails()
    context = {
        'user': user,
        'users_url': request.build_absolute_uri(reverse('auth:users'))
    }
    send_mail(request, 'account/email/request_confirmation', context, emails)


def send_request_activation(request, user):
    '''
    Sends an email to the admins once a users email was validated.
    '''
    emails = get_manager_emails()
    context = {
        'user': user,
        'users_url': request.build_absolute_uri(reverse('auth:users'))
    }
    send_mail(request, 'account/email/request_activation', context, emails)


def send_notify_confirmation(request, user):
    '''
    Sends an email to the admins once a user was confirmed.
    '''
    emails = get_manager_emails()
    context = {
        'user': user,
        'request_user': request.user
    }
    send_mail(request, 'account/email/notify_confirmation', context, emails)


def send_notify_rejection(request, user):
    '''
    Sends an email to the admins once a user was rejected.
    '''
    emails = get_manager_emails()
    context = {
        'user': user,
        'request_user': request.user
    }
    send_mail(request, 'account/email/notify_rejection', context, emails)


def send_notify_activation(request, user):
    '''
    Sends an email to the admins once a user was activated.
    '''
    emails = get_manager_emails()
    context = {
        'user': user,
        'request_user': request.user
    }
    send_mail(request, 'account/email/notify_activation', context, emails)


def send_activation(request, user):
    '''
    Sends an email to the once he/she was activated.
    '''
    context = {
        'user': user,
        'login_url': request.build_absolute_uri(reverse('account_login'))
    }
    send_mail(request, 'account/email/activation', context, [user.email])
