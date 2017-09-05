import logging

from django.conf import settings
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save, m2m_changed

from allauth.account.signals import email_confirmed

from .models import Profile

from .signals import (
    user_created,
    user_updated,
    user_groups_updated,
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
            logger.info('User \'%s\' created.' % user.username)

        elif kwargs['update_fields'] is None:
            # a login triggers this handler with update_fields=last_login
            user_updated.send(sender=User, user=user)
            logger.info('User \'%s\' updated.' % user.username)


@receiver(m2m_changed, sender=User.groups.through)
def m2m_changed_user(sender, **kwargs):
    if not kwargs.get('raw', False):
        user = kwargs['instance']

        # fire the signal only one per change
        if kwargs['action'] in ('post_add', 'post_remove', 'post_clear'):
            user_groups_updated.send(sender=User, user=user)
            logger.info('Groups for user \'%s\' updated.' % user.username)


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
