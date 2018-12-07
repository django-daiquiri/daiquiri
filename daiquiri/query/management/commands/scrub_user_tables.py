from django.conf import settings
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db.utils import ProgrammingError

from rest_framework.exceptions import ValidationError

from daiquiri.core.adapter import DatabaseAdapter
from daiquiri.query.models import QueryJob


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--user', help='Only scrub jobs for this user.')
        parser.add_argument('--delete', action='store_true', help='Delete stale tables.')

    def handle(self, *args, **options):
        if options['user']:
            usernames = [options['user']]
        else:
            usernames = ['anonymous'] + list(User.objects.values_list('username', flat=True))

        adapter = DatabaseAdapter()

        stale_tables = []
        for username in usernames:
            schema_name = settings.QUERY_USER_SCHEMA_PREFIX + username

            tables = adapter.fetch_tables(schema_name)
            jobs = QueryJob.objects.filter(schema_name=schema_name)

            for table in tables:
                job = QueryJob.objects.filter(
                    schema_name=schema_name,
                    table_name=table['name']
                ).first()

                if job and job.phase != QueryJob.PHASE_ARCHIVED:
                    stale_tables.append((schema_name, table['name']))

        if stale_tables:
            print('The following database tables have no associated QueryJob:')

            for stale_table in stale_tables:
                print('* %s.%s' % stale_table)

            if options['delete']:
                for schema_name, table_name in stale_tables:
                    adapter.drop_table(schema_name, table_name)

                print('The tables have been deleted.')
        else:
            print('No tables without associated QueryJob have been found.')
