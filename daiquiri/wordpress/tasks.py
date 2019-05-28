import logging
import subprocess

from django.conf import settings

from celery import shared_task

from daiquiri.core.tasks import Task


def wordpress_cli(*args):
    if settings.WORDPRESS_PATH:
        args = [settings.WORDPRESS_CLI, '--path=%s' % settings.WORDPRESS_PATH] + list(args)
        subprocess.check_output(args, stderr=subprocess.STDOUT)
    elif settings.WORDPRESS_SSH:
        args = [settings.WORDPRESS_CLI, '--ssh=%s' % settings.WORDPRESS_SSH] + list(args)
        subprocess.check_output(args, stderr=subprocess.STDOUT)


@shared_task(base=Task)
def update_wordpress_user(username, email, first_name, last_name):
    try:
        # check if the user already exists
        wordpress_cli('user', 'get', username)

        # update the user
        wordpress_cli('user', 'update', username, '--user_email=%s' % email, '--first_name=%s' % first_name, '--last_name=%s' % last_name)

    except subprocess.CalledProcessError:
        # create the wordpress user
        wordpress_cli('user', 'create', username, email, '--first_name=%s' % first_name, '--last_name=%s' % last_name)


@shared_task(base=Task)
def delete_wordpress_user(username):
    try:
        # delete the user
        wordpress_cli('user', 'delete', username, '--reassign=-1', '--yes')
    except subprocess.CalledProcessError as e:
        logger = logging.getLogger(__name__)
        logger.error('could not delete user %s (%s)', username, e.output)


@shared_task(base=Task)
def update_wordpress_role(username, role):
    try:
        # set the role for the user
        wordpress_cli('user',  'set-role', username, role)
    except subprocess.CalledProcessError:
        pass
