from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from daiquiri.query.models import QueryJob


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('username', help='Remove all query jobs of this user.')
        parser.add_argument('-y', action='store_true', help='Answer yes for all questions.')

    def handle(self, *args, **options):

        if options['username'] == 'anonymous':
            jobs = QueryJob.objects.filter_by_owner(None).exclude(phase=QueryJob.PHASE_ARCHIVED)
        else:
            user = User.objects.get(username=options['username'])
            jobs = QueryJob.objects.filter_by_owner(user).exclude(phase=QueryJob.PHASE_ARCHIVED)

        count = jobs.count()

        if count > 0:
            if options['y']:
                archive = True
            else:
                print('%i jobs found. Really archive these jobs? [yes/no]:' % jobs.count())
                archive = raw_input().lower() in ['yes', 'y']

            if archive:
                for job in jobs:
                    job.archive()
        else:
            print('No jobs found for this user.')
