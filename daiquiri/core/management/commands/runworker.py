import subprocess

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('queue', help='Name of the worker.')
        parser.add_argument('-c', type=int, default=1, help='Concurrency for the worker.')

    def handle(self, *args, **options):
        queue = options['queue']
        concurrency = str(options['c'])

        node = '%s_%s' % (settings.DAIQUIRI_APP, queue)

        args = [
            'celery', 'worker',
            '-A', 'config',
            '-Q', queue,
            '-c', concurrency,
            '-n', node,
            '-l',  'info'
        ]
        subprocess.call(args)
