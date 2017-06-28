from __future__ import absolute_import, unicode_literals

import subprocess

from django.conf import settings

from celery import shared_task


@shared_task
def create_wordpress_user(username, email, first_name, last_name):
    subprocess.check_call([
        settings.WORDPRESS_CLI,
        'user',
        'create',
        username,
        email,
        '--first_name=%s' % first_name,
        '--last_name=%s' % last_name
    ])


@shared_task
def update_wordpress_user(username, email, first_name, last_name):
    subprocess.check_call([
        settings.WORDPRESS_CLI,
        'user',
        'update',
        username,
        '--user_email=%s' % email,
        '--first_name=%s' % first_name,
        '--last_name=%s' % last_name
    ])


@shared_task
def update_wordpress_role(username, role):
    subprocess.check_call([
        settings.WORDPRESS_CLI,
        'user',
        'set-role',
        username,
        role
    ])
