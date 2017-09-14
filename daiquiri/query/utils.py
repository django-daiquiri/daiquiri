import os
import sys

from django.conf import settings
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from daiquiri.core.adapter import get_adapter
from daiquiri.core.utils import human2bytes
from daiquiri.metadata.models import Database, Table, Column, Function


def get_format_config(format_key):
    return [f for f in settings.QUERY_DOWNLOAD_FORMATS if f['key'] == format_key][0]


def get_default_table_name():
    return now().strftime("%Y-%m-%d-%H-%M-%S")


def get_default_queue():
    return settings.QUERY_QUEUES[0]['key']


def get_query_language_choices():
    return [('%(key)s-%(version)s' % item, item['label']) for item in settings.QUERY_LANGUAGES]


def get_queue_choices():
    return [(item['key'], item['label']) for item in settings.QUERY_QUEUES]


def get_tap_schema_name():
    tap_config = settings.DATABASES.get('tap')
    if tap_config:
        return tap_config['NAME']
    else:
        return None


def get_user_database_name(user):
    if not user or user.is_anonymous():
        username = 'anonymous'
    else:
        username = user.username

    return settings.QUERY_USER_DATABASE_PREFIX + username


def get_quota(user):
    if not user or user.is_anonymous():
        anonymous_quota = human2bytes(settings.QUERY_QUOTA.get('anonymous'))
        return anonymous_quota if anonymous_quota else 0

    else:
        user_quota = human2bytes(settings.QUERY_QUOTA.get('user'))
        quota = user_quota if user_quota else 0

        # apply quota for user
        user_quotas = settings.QUERY_QUOTA.get('users')
        if user_quotas:
            user_quota = human2bytes(user_quotas.get(user.username))
            if user_quota:
                quota = user_quota if user_quota > quota else quota

        # apply quota for group
        group_quotas = settings.QUERY_QUOTA.get('groups')
        if group_quotas:
            for group in user.groups.all():
                group_quota = human2bytes(group_quotas.get(group.name))
                if group_quota:
                    quota = group_quota if group_quota > quota else quota

    return quota


def get_download_file_name(user, table_name, format_config):
    if not user or user.is_anonymous():
        username = 'anonymous'
    else:
        username = user.username

    directory_name = os.path.join(settings.QUERY_DOWNLOAD_DIR, username)
    return os.path.join(directory_name, table_name + '.' + format_config['extension'])


def fetch_user_database_metadata(user, jobs):

    database_name = get_user_database_name(user)

    database = {
        'order': sys.maxsize,
        'name': database_name,
        'query_strings': [database_name],
        'description': _('Your personal database'),
        'tables': []
    }

    for job in jobs:
        if job.phase == job.PHASE_COMPLETED:
            table = {
                'name': job.table_name,
                'query_strings': [database_name, job.table_name],
                'columns': job.metadata['columns']
            }

            for column in table['columns']:
                column['query_strings'] = [column['name']]

            database['tables'].append(table)

    return [database]


def get_asterisk_columns(display_column):
    database_name, table_name, _ = display_column[1]
    column_names = get_adapter().database.fetch_column_names(database_name, table_name)
    return [(column_name, (database_name, table_name, column_name)) for column_name in column_names]


def check_permissions(user, keywords, columns, functions):
    messages = []

    # check keywords against whitelist
    for keywords in keywords:
        pass

    # check permissions on databases/tables/columns
    for column in columns:
        database_name, table_name, column_name = column

        # check permission on database
        if database_name is None:
            continue
        elif database_name == get_tap_schema_name():
            continue
        elif database_name == get_user_database_name(user):
            continue
        else:
            try:
                database = Database.objects.filter_by_access_level(user).get(name=database_name)
            except Database.DoesNotExist:
                messages.append(_('Database %s not found.') % database_name)
                continue

        # check permission on table
        if table_name is None:
            continue
        else:
            try:
                table = Table.objects.filter_by_access_level(user).filter(database=database).get(name=table_name)
            except Table.DoesNotExist:
                messages.append(_('Table %s not found.') % table_name)
                continue

        # check permission on column
        if column_name is None:
            continue
        elif column_name == '*':
            columns = Column.objects.filter_by_access_level(user).filter(table=table)
            actual_columns = get_adapter().database.fetch_columns(database_name, table_name)

            column_names_set = set([column.name for column in columns])
            actual_column_names_set = set([column['name'] for column in actual_columns])

            if column_names_set != actual_column_names_set:
                messages.append(_('The asterisk (*) is not allowed for this table.'))
                continue
        else:
            try:
                column = Column.objects.filter_by_access_level(user).filter(table=table).get(name=column_name)
            except Column.DoesNotExist:
                messages.append(_('Column %s not found.') % column_name)
                continue



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
