import sys

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from daiquiri.core.adapter import get_adapter
from daiquiri.uws.settings import PHASE_COMPLETED


def get_user_database_name(username):
    return settings.QUERY['user_database_prefix'] + username


def fetch_user_database_metadata(jobs, username):
    adapter = get_adapter('data')

    database_name = get_user_database_name(username)

    database = {
        'order': sys.maxsize,
        'name': database_name,
        'query_string': adapter.escape_identifier(database_name),
        'description': _('Your personal database'),
        'tables': []
    }

    for job in jobs:
        if job.phase == PHASE_COMPLETED:
            table = job.metadata
            table['query_string'] = '%(database)s.%(table)s' % {
                'database': adapter.escape_identifier(database_name),
                'table': adapter.escape_identifier(table['name'])
            }

            for column in table['columns']:
                column['query_string'] = adapter.escape_identifier(column['name'])

            database['tables'].append(table)

    return database
