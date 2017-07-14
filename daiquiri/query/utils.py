import os
import sys

from django.conf import settings
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from daiquiri.core.adapter import get_adapter
from daiquiri.uws.settings import PHASE_COMPLETED


def get_default_table_name():
    return now().strftime("%Y-%m-%d-%H-%M-%S")


def get_user_database_name(user):
    if not user:
        username = '%'
    elif user.is_anonymous():
        username = 'anonymous'
    else:
        username = user.username

    return settings.QUERY['user_database_prefix'] + username


def get_download_file_name(database_name, table_name, username, format):
    directory_name = os.path.join(settings.QUERY['download_dir'], username)
    return os.path.join(directory_name, table_name + '.' + format['extension'])


def fetch_user_database_metadata(user, jobs):
    adapter = get_adapter('data')

    database_name = get_user_database_name(user)

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

    return [database]
