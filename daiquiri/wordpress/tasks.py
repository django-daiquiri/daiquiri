from __future__ import absolute_import, unicode_literals

import subprocess

from django.conf import settings

from celery import shared_task

from daiquiri.core.tasks import Task


@shared_task(base=Task)
def create_wordpress_user(username, email, first_name, last_name):
    return subprocess.check_output([
        settings.WORDPRESS_CLI,
        'user',
        'create',
        username,
        email,
        '--first_name=%s' % first_name,
        '--last_name=%s' % last_name,
        '--path=%s' % settings.WORDPRESS_PATH
    ])


@shared_task(base=Task)
def update_wordpress_user(username, email, first_name, last_name):
    return subprocess.check_output([
        settings.WORDPRESS_CLI,
        'user',
        'update',
        username,
        '--user_email=%s' % email,
        '--first_name=%s' % first_name,
        '--last_name=%s' % last_name,
        '--path=%s' % settings.WORDPRESS_PATH
    ])


@shared_task(base=Task)
def update_wordpress_role(username, role):
    return subprocess.check_output([
        settings.WORDPRESS_CLI,
        'user',
        'set-role',
        username,
        role,
        '--path=%s' % settings.WORDPRESS_PATH
    ])
