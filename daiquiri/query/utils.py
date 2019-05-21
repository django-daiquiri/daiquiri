import os
import sys

from django.conf import settings
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from daiquiri.core.adapter import DatabaseAdapter
from daiquiri.core.utils import human2bytes
from daiquiri.metadata.models import Table, Column


def get_format_config(format_key):

    for format_config in settings.QUERY_DOWNLOAD_FORMATS:
        if format_config['key'] == format_key:
            return format_config

    return None


def get_default_table_name():
    return now().strftime("%Y-%m-%d-%H-%M-%S-%f")


def get_user_schema_name(user):
    if not user or user.is_anonymous:
        username = 'anonymous'
    else:
        username = user.username

    return settings.QUERY_USER_SCHEMA_PREFIX + username


def get_quota(user):
    if not user or user.is_anonymous:
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
    if not user or user.is_anonymous:
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


def get_indexed_objects():
    indexed_objects = {}

    for column in Column.objects.exclude(index_for=''):
        # TODO implement xtype 'spoint' properly

        #if column.datatype not in indexed_objects:
        #    indexed_objects[column.datatype] = [column.indexed_columns]
        #else:
        #    indexed_objects[column.datatype].append(column.indexed_columns)

        if 'spoint' not in indexed_objects:
            indexed_objects['spoint'] = [column.indexed_columns]
        else:
            indexed_objects['spoint'].append(column.indexed_columns)

    return indexed_objects


def get_job_sources(job):
    sources = []

    if 'tables' in job.metadata:
        for schema_name, table_name in job.metadata['tables']:
            table = {
                'schema_name': schema_name,
                'table_name': table_name
            }

            # fetch additional metadata from the metadata store
            try:
                original_table = Table.objects.get(
                    name=table_name,
                    schema__name=schema_name
                )

                if settings.METADATA_BASE_URL:
                    metadata_url = '%s/%s/%s' % (settings.METADATA_BASE_URL.strip('/'), schema_name, table_name)
                else:
                    metadata_url = ''

                table.update({
                    'title': original_table.title,
                    'description': original_table.description,
                    'attribution': original_table.attribution,
                    'license': original_table.license,
                    'doi': original_table.doi,
                    'url': metadata_url
                })

                sources.append(table)

            except Table.DoesNotExist:
                pass

    return sources


def get_job_column(job, display_column_name):
    try:
        schema_name, table_name, column_name = \
            job.metadata['display_columns'][display_column_name]
    except (ValueError, KeyError):
        return {}

    try:
        column = Column.objects.get(
            name=column_name,
            table__name=table_name,
            table__schema__name=schema_name
        )

        return {
            'name': column.name,
            'description': column.description,
            'unit': column.unit,
            'ucd': column.ucd,
            'utype': column.utype,
            'datatype': column.datatype,
            'arraysize': column.arraysize,
            'principal': column.principal,
            'indexed': False,
            'std': column.std
        }

    except Column.DoesNotExist:
        return {}


def get_job_columns(job):
    columns = []

    if job.phase == job.PHASE_COMPLETED:
        database_columns = DatabaseAdapter().fetch_columns(job.schema_name, job.table_name)

        for database_column in database_columns:
            column = get_job_column(job, database_column['name'])
            column.update(database_column)
            columns.append(column)

    else:
        for display_column in job.metadata['display_columns']:
            columns.append(get_job_column(job, display_column))

    return columns
