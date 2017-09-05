from django.conf import settings
from django.dispatch import receiver

from allauth.account.signals import email_confirmed

from .signals import (
    user_confirmed,
    user_rejected,
    user_activated
)

from .utils import (
    send_request_confirmation,
    send_request_activation,
    send_notify_confirmation,
    send_notify_rejection,
    send_notify_activation,
    send_activation
)


@receiver(email_confirmed)
def email_confirmed_handler(sender, **kwargs):
    '''
    Sends an email to the admins when a user has validated his/her email address.
    '''
    if settings.AUTH_WORKFLOW:
        user = kwargs['email_address'].user

        if user.profile.is_pending:
            if settings.AUTH_WORKFLOW == 'confirmation':
                send_request_confirmation(kwargs['request'], user)
            elif settings.AUTH_WORKFLOW == 'activation':
                send_request_activation(kwargs['request'], user)


@receiver(user_confirmed)
def user_confirmed_handler(sender, **kwargs):
    '''
    Sends an email to the admins when a user was confirmed by a manager.
    '''
    if settings.AUTH_WORKFLOW:
        send_notify_confirmation(kwargs['request'], kwargs['user'])


@receiver(user_rejected)
def user_rejected_handler(sender, **kwargs):
    '''
    Sends an email to the admins when a user was rejected by a manager.
    '''
    if settings.AUTH_WORKFLOW:
        send_notify_rejection(kwargs['request'], kwargs['user'])


@receiver(user_activated)
def user_activated_handler(sender, **kwargs):
    '''
    Sends an email to the user and another email to the admins once a user was activated by an admin.
    '''
    if settings.AUTH_WORKFLOW:
        send_notify_activation(kwargs['request'], kwargs['user'])
        send_activation(kwargs['request'], kwargs['user'])
