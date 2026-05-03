from datetime import datetime

from django.core.management.base import BaseCommand
from django.db.models import Max, Min
from django.utils import timezone

from daiquiri.query.models import QueryJob


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            '--delete', action='store_true', help='Actually delete the expired jobs'
        )

    def handle(self, *args, **opts):
        queryset = QueryJob.objects.filter(
            destruction_time__isnull=False,
            destruction_time__lte=timezone.now()
        )

        if queryset.count() == 0:
            self.stdout.write('No expired query jobs found')
            return

        stats = queryset.aggregate(
            oldest=Min('creation_time'),
            newest=Max('creation_time'),
        )
        oldest = datetime.isoformat(stats['oldest'], timespec='seconds') if stats['oldest'] else 'N/A'
        newest = datetime.isoformat(stats['newest'], timespec='seconds') if stats['newest'] else 'N/A'

        self.stdout.write(f'Jobs found: {queryset.count()}')
        self.stdout.write(f'Affected users: {queryset.values("owner").distinct().count()}')
        self.stdout.write(f'Newest job was created on {newest}')
        self.stdout.write(f'Oldest job was created on {oldest}')

        if opts['delete']:
            deleted, _ = queryset.delete()
            self.stdout.write(f'Deleted {deleted} jobs.')
        else:
            self.stdout.write('(use --delete to actually remove them)')
