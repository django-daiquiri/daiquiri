import re
from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from daiquiri.query.models import QueryJob


class Command(BaseCommand):

    pattern = re.compile(r'(\d+)([dsmhw])')

    def add_arguments(self, parser):
        parser.add_argument('username', help='Remove all query jobs of this user.')
        parser.add_argument('-k', '--keep', default=None, help='Keep jobs newer than this timespan.')
        parser.add_argument('-y', '--yes', action='store_true', help='Answer yes for all questions.')

    def handle(self, *args, **options):

        # parse username -> owner
        if options['username'] == 'anonymous':
            owner = None
        else:
            try:
                owner = User.objects.get(username=options['username'])
            except User.DoesNotExist as e:
                raise CommandError('User "{}" does not exist'.format(options['username'])) from e

        # parse keep -> before
        if options['keep']:
            match = self.pattern.match(options['keep'])
            if match:
                value, attribute = int(match.group(1)), match.group(2)

                if attribute == 'd':
                    delta = timedelta(days=value)
                elif attribute == 's':
                    delta = timedelta(seconds=value)
                elif attribute == 'm':
                    delta = timedelta(minutes=value)
                elif attribute == 'h':
                    delta = timedelta(hours=value)
                elif attribute == 'w':
                    delta = timedelta(weeks=value)

                before = datetime.now() - delta

            else:
                raise CommandError('User "{}" does not exist'.format(options['username']))
        else:
            before = None

        # get the jobs queryset
        jobs = QueryJob.objects.filter_by_owner(owner).exclude(phase=QueryJob.PHASE_ARCHIVED)

        if before:
            jobs = jobs.exclude(creation_time__gt=before)

        count = jobs.count()
        if count > 0:
            if options['yes']:
                archive = True
            else:
                print('%i jobs found. Really archive these jobs? [yes/no]:' % jobs.count())
                archive = input().lower() in ['yes', 'y']

            if archive:
                for job in jobs:
                    job.archive()
        else:
            print('No jobs found for this user.')
