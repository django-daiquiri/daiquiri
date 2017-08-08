import subprocess

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('queue', help='Name of the worker.')
        parser.add_argument('concurrency', type=int, help='Concurrency for the worker.')

    def handle(self, *args, **options):
        queue = options['queue']
        concurrency = str(options['concurrency'])

        node = '%s_%s' % (settings.DAIQUIRI_APP, queue)

        args = ['celery', 'worker', '-A', settings.DAIQUIRI_APP, '-Q', queue, '-c', concurrency, '-n', node, '-l',  'info']
        subprocess.call(args)
