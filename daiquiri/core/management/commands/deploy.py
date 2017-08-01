import os
import subprocess

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def handle(self, *args, **options):

        call_command('collectstatic', '--noinput')
        subprocess.call(['touch', os.path.join(settings.PROJECT_DIR, 'wsgi.py')])
