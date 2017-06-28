from django.dispatch import receiver

from allauth.account.signals import email_confirmed

from .signals import (
    user_confirmed,
    user_activated
)

from .utils import (
    get_account_workflow,
    send_request_confirmation,
    send_request_activation,
    send_notify_confirmation,
    send_notify_activation,
    send_activation
)


@receiver(email_confirmed)
def email_confirmed_handler(sender, **kwargs):
    account_workflow = get_account_workflow()

    if account_workflow:
        user = kwargs['email_address'].user

        if user.profile.is_pending:
            if account_workflow == 'confirmation':
                send_request_confirmation(kwargs['request'], kwargs['email_address'].user)
            elif account_workflow == 'activation':
                send_request_activation(kwargs['request'], kwargs['email_address'].user)


@receiver(user_confirmed)
def user_confirmed_handler(sender, **kwargs):
    send_notify_confirmation(kwargs['request'], kwargs['user'])


@receiver(user_activated)
def user_activated_handler(sender, **kwargs):
    send_notify_activation(kwargs['request'], kwargs['user'])
    send_activation(kwargs['request'], kwargs['user'])
