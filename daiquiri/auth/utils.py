from django.urls import reverse

from daiquiri.core.utils import get_admin_emails, get_permission_emails, send_mail


def get_full_name(user):
    if user.first_name and user.last_name:
        return user.first_name + ' ' + user.last_name
    else:
        return user.username


def get_manager_emails():
    return get_permission_emails((
        'daiquiri_auth.view_profile',
    ))


def send_request_confirmation(request, user):
    '''
    Sends an email to the admins once a users email was validated.
    '''
    send_mail(request, 'account/email/request_confirmation', {
        'user': user,
        'users_url': request.build_absolute_uri(reverse('auth:users'))
    }, get_manager_emails())


def send_request_activation(request, user):
    '''
    Sends an email to the admins once a users email was validated.
    '''
    send_mail(request, 'account/email/request_activation', {
        'user': user,
        'users_url': request.build_absolute_uri(reverse('auth:users'))
    }, get_manager_emails())


def send_notify_confirmation(request, user):
    '''
    Sends an email to the admins once a user was confirmed.
    '''
    send_mail(request, 'account/email/notify_confirmation', {
        'user': user,
        'request_user': request.user
    }, get_manager_emails())


def send_notify_rejection(request, user):
    '''
    Sends an email to the admins once a user was rejected.
    '''
    send_mail(request, 'account/email/notify_rejection', {
        'user': user,
        'request_user': request.user
    }, get_manager_emails())


def send_notify_activation(request, user):
    '''
    Sends an email to the admins once a user was activated.
    '''
    send_mail(request, 'account/email/notify_activation', {
        'user': user,
        'request_user': request.user
    }, get_manager_emails())


def send_activation(request, user):
    '''
    Sends an email to the once he/she was activated.
    '''
    send_mail(request, 'account/email/activation', {
        'user': user,
        'login_url': request.build_absolute_uri(reverse('account_login'))
    }, [user.email])


def send_notify_password_changed(request, user):
    '''
    Sends an email to the admins once a user updated his/her account.
    '''
    send_mail(request, 'account/email/notify_password_changed', {
        'user': user
    }, get_admin_emails())
