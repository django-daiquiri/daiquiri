import os
import sys

from django.conf import settings
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from daiquiri.core.adapter import get_adapter
from daiquiri.metadata.models import Database, Table, Column, Function


def get_default_table_name():
    return now().strftime("%Y-%m-%d-%H-%M-%S")


def get_default_queue():
    return settings.QUERY['queues'][0]['key']


def get_query_language_choices():
    return [('%(key)s-%(version)s' % item, item['label']) for item in settings.QUERY['query_languages']]


def get_queue_choices():
    return [(item['key'], item['label']) for item in settings.QUERY['queues']]


def get_user_database_name(user):
    if not user or user.is_anonymous():
        username = 'anonymous'
    else:
        username = user.username

    return settings.QUERY['user_database_prefix'] + username


def get_download_file_name(database_name, table_name, username, format):
    directory_name = os.path.join(settings.QUERY['download_dir'], username)
    return os.path.join(directory_name, table_name + '.' + format['extension'])


def fetch_user_database_metadata(user, jobs):
    adapter = get_adapter()

    database_name = get_user_database_name(user)

    database = {
        'order': sys.maxsize,
        'name': database_name,
        'query_string': adapter.database.escape_identifier(database_name),
        'description': _('Your personal database'),
        'tables': []
    }

    for job in jobs:
        if job.phase == job.PHASE_COMPLETED:
            table = job.metadata
            table['query_string'] = '%(database)s.%(table)s' % {
                'database': adapter.database.escape_identifier(database_name),
                'table': adapter.database.escape_identifier(table['name'])
            }

            for column in table['columns']:
                column['query_string'] = adapter.database.escape_identifier(column['name'])

            database['tables'].append(table)

    return [database]


def check_permissions(user, keywords, columns, functions):
    messages = []

    # check keywords against whitelist
    for keywords in keywords:
        pass

    # check permissions on databases/tables/columns
    for column in columns:
        try:
            database_name, table_name, column_name = column.split('.')

            # check permission on database
            try:
                database = Database.objects.filter_by_access_level(user).get(name=database_name)
            except Database.DoesNotExist:
                messages.append(_('Database %s not found.') % database_name)
                continue

            # check permission on table
            try:
                table = Table.objects.filter_by_access_level(user).filter(database=database).get(name=table_name)
            except Table.DoesNotExist:
                messages.append(_('Table %s not found.') % table_name)
                continue

            # check permission on column
            try:
                column = Column.objects.filter_by_access_level(user).filter(table=table).get(name=column_name)
            except Column.DoesNotExist:
                messages.append(_('Column %s not found.') % column_name)
                continue

        except ValueError:
            messages.append(_('No database given for column %s') % column)

    # check permissions on functions
    for function_name in functions:
        if function_name.upper() in get_adapter().database.FUNCTIONS:
            continue
        else:
            # check permission on function
            function = Function.objects.filter_by_access_level(user).get(name=function_name)
            if not function:
                messages.append(_('Function %s not found.') % function_name)
                continue

    # return the error stack
    return list(set(messages))
