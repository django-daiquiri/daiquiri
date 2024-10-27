import subprocess

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('queue', nargs='?', default='default', help='Name of the worker [default=default].')

    def handle(self, *args, **options):
        key = options['queue']
        hostname = f'{settings.DAIQUIRI_APP}_{key}@%h'

        try:
            queue = next(filter(lambda q: q['key'] == key, settings.QUEUES))
        except StopIteration:
            try:
                queue = next(filter(lambda q: q['key'] == key, settings.QUERY_QUEUES))
            except StopIteration as e:
                raise CommandError(f'Queue "{key}" does not exist') from e

        args = [
            'celery',
            '-A', 'config',
            'worker',
            '-Q', key,
            '-c', str(queue.get('concurrency', 1)),
            '-n', hostname,
            '-l', 'info'
        ]

        subprocess.call(args)
