import subprocess

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('operation', choices=[
            'start',
            'stop',
            'stopwait',
            'kill',
            'restart'
        ])

    def handle(self, *args, **options):
        if not settings.CELERY_PIDFILE_PATH:
            raise CommandError('CELERY_PIDFILE_PATH is not set')

        queues = [
            {
                'node': '{}_default'.format(settings.DAIQUIRI_APP),
                'queue': 'default',
                'concurency': 1
            },
            {
                'node': '{}_download'.format(settings.DAIQUIRI_APP),
                'queue': 'download',
                'concurency': 1
            }
        ] + [{
            'node': '{}_query_{}'.format(settings.DAIQUIRI_APP, queue['key']),
            'queue': 'query_{}'.format(queue['key']),
            'concurency': queue.get('concurency', 1)
        } for queue in settings.QUERY_QUEUES]

        args = [settings.CELERY_BIN, '-A', 'config', 'multi', options['operation']]
        args += [queue['node'] for queue in queues]

        if options['operation'] in ['start', 'restart']:
            for queue in queues:
                args += [
                    '-Q:{}'.format(queue['node']), queue['queue'],
                    '-c:{}'.format(queue['node']), str(queue['concurency'])
                ]

        args += [
            '--pidfile={}/%n.pid'.format(settings.CELERY_PIDFILE_PATH),
            '--loglevel={}'.format(settings.CELERY_LOG_LEVEL)
        ]
        if settings.CELERY_LOG_PATH:
            args += [
                '--logfile={}/%n.log'.format(settings.CELERY_LOG_PATH)
            ]

        subprocess.call(args)
