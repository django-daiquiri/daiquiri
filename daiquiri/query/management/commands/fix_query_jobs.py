from django.core.management.base import BaseCommand
from django.db.utils import ProgrammingError

from rest_framework.exceptions import ValidationError

from daiquiri.core.adapter import DatabaseAdapter
from daiquiri.query.models import QueryJob


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--user', help='Only fix jobs for this user.')
        parser.add_argument('--queue', help='Name of the queue to use.')
        parser.add_argument('--dry', action='store_true', help='Perform a dryrun.')

    def handle(self, *args, **options):
        # look for completed jobs with no table
        queryset = QueryJob.objects.filter(phase=QueryJob.PHASE_COMPLETED)

        if options['user']:
            queryset = queryset.filter(owner__username=options['user'])

        for job in queryset:
            try:
                DatabaseAdapter().fetch_size(job.schema_name, job.table_name)
            except ProgrammingError:
                try:
                    job.phase = QueryJob.PHASE_PENDING

                    if options['queue']:
                        job.queue = options['queue']

                    job.process()

                    print(f'Run {job.id} by {job.owner} again.')

                    if not options['dry']:
                        job.run()

                except ValidationError as e:
                    job.phase = QueryJob.PHASE_ERROR

                    job.error_summary = ''
                    for key, errors in e.detail.items():
                        try:
                            job.error_summary += ''.join(errors['messages'])
                        except TypeError:
                            job.error_summary += ''.join(errors)

                    print(f'Error for {job.id} by {job.owner}: {job.error_summary}')

                    if not options['dry']:
                        job.save()
