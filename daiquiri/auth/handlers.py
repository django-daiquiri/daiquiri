import logging

from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import m2m_changed, post_delete, post_save
from django.dispatch import receiver

from allauth.account.signals import email_confirmed, password_changed, password_reset

from .models import Profile
from .signals import (
    user_activated,
    user_confirmed,
    user_created,
    user_deleted,
    user_disabled,
    user_enabled,
    user_groups_updated,
    user_rejected,
    user_updated,
)
from .utils import (
    send_activation,
    send_notify_activation,
    send_notify_confirmation,
    send_notify_password_changed,
    send_notify_rejection,
    send_request_activation,
    send_request_confirmation,
)

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def post_save_user(sender, **kwargs):
    if not kwargs.get('raw', False):
        user = kwargs['instance']

        if kwargs['created']:
            profile = Profile()
            profile.user = user
            profile.save()

            user_created.send(sender=User, user=user)
            logger.info('user \'%s\' created.', user.username)

        elif kwargs['update_fields'] is None:
            # a login triggers this handler with update_fields=last_login
            user_updated.send(sender=User, user=user)
            logger.info('user \'%s\' updated.', user.username)


@receiver(post_delete, sender=User)
def post_delete_user(sender, **kwargs):
    if not kwargs.get('raw', False):
        user = kwargs['instance']
        user_deleted.send(sender=User, user=user)
        logger.info('user \'%s\' deleted.', user.username)


@receiver(m2m_changed, sender=User.groups.through)
def m2m_changed_user(sender, **kwargs):
    if not kwargs.get('raw', False):
        user = kwargs['instance']

        # fire the signal only one per change
        if kwargs['action'] in ('post_add', 'post_remove', 'post_clear'):
            user_groups_updated.send(sender=User, user=user)
            logger.info('groups for user \'%s\' updated.', user.username)


@receiver(email_confirmed)
def email_confirmed_handler(sender, **kwargs):
    '''
    Gets notified when a user has validated his/her email address.
    '''
    request = kwargs['request']
    user = kwargs['email_address'].user

    logger.info('user \'%s\' validated his/her email address.', user.username)

    if settings.AUTH_WORKFLOW:
        user = kwargs['email_address'].user

        if user.profile.is_pending:
            if settings.AUTH_WORKFLOW == 'confirmation':
                send_request_confirmation(request, user)
            elif settings.AUTH_WORKFLOW == 'activation':
                send_request_activation(request, user)


@receiver(user_confirmed)
def user_confirmed_handler(sender, **kwargs):
    '''
    Gets notified when a user was confirmed by a manager.
    '''
    request = kwargs['request']
    user = kwargs['user']

    logger.info('user \'%s\' confirmed by \'%s\'.', user.username, request.user.username)
    if settings.AUTH_WORKFLOW:
        send_notify_confirmation(request, user)


@receiver(user_rejected)
def user_rejected_handler(sender, **kwargs):
    '''
    Gets notified when a user was rejected by a manager.
    '''
    request = kwargs['request']
    user = kwargs['user']

    logger.info('user \'%s\' rejected by \'%s\'.', user.username, request.user.username)
    if settings.AUTH_WORKFLOW:
        send_notify_rejection(request, user)


@receiver(user_activated)
def user_activated_handler(sender, **kwargs):
    '''
    Gets notified when a user was activated by an admin.
    '''
    request = kwargs['request']
    user = kwargs['user']

    logger.info('user \'%s\' activated by \'%s\'.', user.username, request.user.username)
    if settings.AUTH_WORKFLOW:
        send_notify_activation(request, user)
        send_activation(request, user)


@receiver(user_disabled)
def user_disabled_handler(sender, **kwargs):
    '''
    Gets notified when a user was disabled by a manager.
    '''
    request = kwargs['request']
    user = kwargs['user']

    logger.info('user \'%s\' disabled by \'%s\'.', user.username, request.user.username)


@receiver(user_enabled)
def user_enabled_handler(sender, **kwargs):
    '''
    Gets notified when a user was disabled by a manager.
    '''
    request = kwargs['request']
    user = kwargs['user']

    logger.info('user \'%s\' enabled by \'%s\'.', user.username, request.user.username)


@receiver(password_changed)
@receiver(password_reset)
def password_changed_handler(sender, **kwargs):
    '''
    Gets notified when a user was disabled by a manager.
    '''
    request = kwargs['request']
    user = kwargs['user']

    logger.info('user \'%s\' changed his/her password.', user.username)
    if settings.AUTH_WORKFLOW == 'confirmation':
        send_notify_password_changed(request, user)
