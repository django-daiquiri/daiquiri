from django.dispatch import receiver

from daiquiri.auth.signals import (
    user_created,
    user_updated,
    user_groups_updated
)

from .utils import (
    create_wordpress_user,
    update_wordpress_user,
    update_wordpress_role
)


@receiver(user_created)
def user_created_handler(sender, **kwargs):
    create_wordpress_user(kwargs['user'])


@receiver(user_updated)
def user_updated_handler(sender, **kwargs):
    update_wordpress_user(kwargs['user'])


@receiver(user_groups_updated)
def user_groups_updated_handler(sender, **kwargs):
    update_wordpress_role(kwargs['user'])
