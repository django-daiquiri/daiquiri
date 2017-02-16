import sys

from django.utils.translation import ugettext_lazy as _

from daiquiri_core.adapter import get_adapter
from daiquiri_query.backends import get_query_backend


def fetch_user_database_metadata(jobs, username):
    adapter = get_adapter('data')
    query_backend = get_query_backend()

    database_name = query_backend.get_user_database_name(username)

    database = {
        'order': sys.maxsize,
        'name': database_name,
        'query_string': adapter.escape_identifier(database_name),
        'description': _('Your personal database'),
        'tables': []
    }

    for job in jobs:
        table = job.metadata
        table['query_string'] = '%(database)s.%(table)s' % {
            'database': adapter.escape_identifier(database_name),
            'table': adapter.escape_identifier(table['name'])
        }

        for column in table['columns']:
            column['query_string'] = adapter.escape_identifier(column['name'])

        database['tables'].append(table)

    return database
