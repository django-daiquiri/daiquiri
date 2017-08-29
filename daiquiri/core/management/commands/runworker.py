import subprocess

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('queue', nargs='?', default='default', help='Name of the worker [default=default].')
        parser.add_argument('-c', type=int, default=1, help='Concurrency for the worker.')

    def handle(self, *args, **options):
        concurrency = str(options['c'])

        queue = '%s_%s' % (settings.DAIQUIRI_APP, options['queue'])

        args = [
            'celery', 'worker',
            '-A', 'config',
            '-Q', queue,
            '-c', concurrency,
            '-n', queue,
            '-l',  'info'
        ]

        subprocess.call(args)
