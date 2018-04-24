from django.conf import settings

from .tasks import (
    update_wordpress_user as update_wordpress_user_task,
    update_wordpress_role as update_wordpress_role_task
)


def update_wordpress_user(user):
    if not settings.ASYNC:
        update_wordpress_user_task.apply((user.username, user.email, user.first_name, user.last_name), throw=True)
    else:
        update_wordpress_user_task.apply_async((user.username, user.email, user.first_name, user.last_name))


def update_wordpress_role(user):
    if user.is_superuser:
        wordpress_role = 'administrator'
    elif user.groups.filter(name='wordpress_admin').exists():
        wordpress_role = 'administrator'
    elif user.groups.filter(name='wordpress_editor').exists():
        wordpress_role = 'editor'
    else:
        wordpress_role = 'subscriber'

    if not settings.ASYNC:
        update_wordpress_role_task.apply((user.username, wordpress_role), throw=True)
    else:
        update_wordpress_role_task.apply_async((user.username, wordpress_role))
