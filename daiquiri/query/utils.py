import sys

from django.conf import settings
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from daiquiri.core.adapter import DatabaseAdapter
from daiquiri.core.utils import human2bytes
from daiquiri.metadata.models import Schema, Table, Column, Function


def get_format_config(format_key):

    for format_config in settings.QUERY_DOWNLOAD_FORMATS:
        if format_config['key'] == format_key:
            return format_config

    return None


def get_default_table_name():
    return now().strftime("%Y-%m-%d-%H-%M-%S")


def get_query_language_choices():
    return [('%(key)s-%(version)s' % item, item['label']) for item in settings.QUERY_LANGUAGES]


def get_queue_choices():
    return [(item['key'], item['label']) for item in settings.QUERY_QUEUES]


def get_user_schema_name(user):
    if not user or user.is_anonymous():
        username = 'anonymous'
    else:
        username = user.username

    return settings.QUERY_USER_SCHEMA_PREFIX + username


def get_quota(user):
    if not user or user.is_anonymous():
        quota = human2bytes(settings.QUERY_QUOTA.get('anonymous'))

    else:
        quota = human2bytes(settings.QUERY_QUOTA.get('user'))

        # apply quota for user
        users = settings.QUERY_QUOTA.get('users')
        if users:
            user_quota = human2bytes(users.get(user.username))
            quota = user_quota if user_quota > quota else quota

        # apply quota for group
        groups = settings.QUERY_QUOTA.get('groups')
        if groups:
            for group in user.groups.all():
                group_quota = human2bytes(groups.get(group.name))
                quota = group_quota if group_quota > quota else quota

    return quota


def get_max_active_jobs(user):
    if not user or user.is_anonymous():
        count = int(settings.QUERY_MAX_ACTIVE_JOBS.get('anonymous') or 0)

    else:
        count = int(settings.QUERY_MAX_ACTIVE_JOBS.get('user') or 0)

        # apply quota for user
        users = int(settings.QUERY_MAX_ACTIVE_JOBS.get('users') or 0)
        if users:
            user_count = int(users.get(user.username))
            count = user_count if user_count and user_count > count else count

        # apply quota for group
        groups = int(settings.QUERY_MAX_ACTIVE_JOBS.get('groups') or 0)
        if groups:
            for group in user.groups.all():
                group_count = int(groups.get(group.name))
                count = group_count if group_count and group_count > count else count

    return count


def fetch_user_schema_metadata(user, jobs):

    schema_name = get_user_schema_name(user)

    schema = {
        'order': sys.maxsize,
        'name': schema_name,
        'query_strings': [schema_name],
        'description': _('Your personal schema'),
        'tables': []
    }

    for job in jobs:
        if job.phase == job.PHASE_COMPLETED:
            table = {
                'name': job.table_name,
                'query_strings': [schema_name, job.table_name]
            }

            if job.metadata:
                table['columns'] = job.metadata.get('columns', {})

                for column in table['columns']:
                    column['query_strings'] = [column['name']]

            schema['tables'].append(table)

    return [schema]


def get_asterisk_columns(display_column):
    schema_name, table_name, _ = display_column[1]
    column_names = DatabaseAdapter().fetch_column_names(schema_name, table_name)
    return [(column_name, (schema_name, table_name, column_name)) for column_name in column_names]


def get_indexed_objects():
    indexed_objects = {}

    for column in Column.objects.exclude(index_for=''):
        if column.datatype not in indexed_objects:
            indexed_objects[column.datatype] = [column.indexed_columns]
        else:
            indexed_objects[column.datatype].append(column.indexed_columns)

    return indexed_objects


def check_permissions(user, keywords, tables, columns, functions):
    messages = []

    # check keywords against whitelist
    for keywords in keywords:
        pass

    # loop over tables to check permissions on schemas/tables
    for schema_name, table_name in tables:

        # check permission on schema
        if schema_name is None:
            # schema_name must not be null, move to next table
            messages.append(_('No schema given for table %s.') % table_name)
            continue
        elif schema_name in [settings.TAP_SCHEMA, get_user_schema_name(user)]:
            # all tables are allowed move to next table
            continue
        else:
            # check permissions on the schema
            try:
                schema = Schema.objects.filter_by_access_level(user).get(name=schema_name)
            except Schema.DoesNotExist:
                # schema not found or not allowed, move to next table
                messages.append(_('Schema %s not found.') % schema_name)
                continue

        # check permission on table
        if table_name is None:
            # table_name must not be null, move to next table
            messages.append(_('No table given for schema %s.') % schema_name)
            continue
        else:
            try:
                Table.objects.filter_by_access_level(user).filter(schema=schema).get(name=table_name)
            except Table.DoesNotExist:
                # table not found or not allowed, move to next table
                messages.append(_('Table %s not found.') % table_name)
                continue

    # loop over columns to check permissions or just to see if they are there,
    # but only if no error messages where appended so far
    if not messages:

        for schema_name, table_name, column_name in columns:

            if schema_name in [None, settings.TAP_SCHEMA, get_user_schema_name(user)] \
                or table_name is None \
                or column_name is None:
                # doesn't need to be checked, move to next column
                continue
            else:
                if not settings.METADATA_COLUMN_PERMISSIONS:
                    # just check if the column exist
                    if column_name == '*':
                        # doesn't need to be checked, move to next table
                        continue

                    else:
                        try:
                            Column.objects.filter(table__schema__name=schema_name).filter(table__name=table_name).get(name=column_name)
                        except Column.DoesNotExist:
                            messages.append(_('Column %s not found.') % column_name)
                            continue
                else:
                    try:
                        schema = Schema.objects.filter_by_access_level(user).get(name=schema_name)
                    except Schema.DoesNotExist:
                        messages.append(_('Schema %s not found.') % schema_name)
                        continue

                    try:
                        table = Table.objects.filter_by_access_level(user).filter(schema=schema).get(name=table_name)
                    except Table.DoesNotExist:
                        messages.append(_('Table %s not found.') % table_name)
                        continue

                    if column_name == '*':
                        columns = Column.objects.filter_by_access_level(user).filter(table=table)
                        actual_columns = DatabaseAdapter().fetch_columns(schema_name, table_name)

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

        # check permission on function
        queryset = Function.objects.filter(name=function_name)

        # forbit the function if it is in metadata.functions, and the user doesn't have access.
        if queryset and not queryset.filter_by_access_level(user):
            messages.append(_('Function %s is not allowed.') % function_name)
        else:
            continue

    # return the error stack
    return list(set(messages))
