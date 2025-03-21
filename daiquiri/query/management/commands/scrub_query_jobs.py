from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from daiquiri.core.adapter import DatabaseAdapter
from daiquiri.query.models import QueryJob


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--user', help='Only scrub jobs for this user.')
        parser.add_argument('--archive', action='store_true', help='Archive stale jobs.')

    def handle(self, *args, **options):
        if options['user']:
            if options['user'] == 'anonymous':
                owners = [None]
            else:
                owners = [User.objects.get(username=options['user'])]

        else:
            owners = [None, *list(User.objects.all())]

        adapter = DatabaseAdapter()

        stale_jobs = []
        for owner in owners:
            jobs = QueryJob.objects.filter(owner=owner)
            for job in jobs:
                if job.phase == job.PHASE_COMPLETED:
                    if not adapter.fetch_table(job.schema_name, job.table_name):
                        stale_jobs.append(job)

        if stale_jobs:
            print('The following QueryJobs have no associated database table:')

            for job in stale_jobs:
                username = job.owner.username if job.owner else 'anonymous'
                print(f'{job.id} by {username} -> {job.schema_name}.{job.table_name}')

            if options['archive']:
                for job in stale_jobs:
                    job.archive()

                print('The jobs have been archived.')
        else:
            print('No QueryJobs without associated associated database table have been found.')
