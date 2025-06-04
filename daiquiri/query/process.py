import json
from collections import OrderedDict

from django.conf import settings
from django.core.cache import cache
from django.utils.translation import gettext as _
from queryparser.adql import ADQLQueryTranslator
from queryparser.exceptions import QueryError, QuerySyntaxError
from rest_framework.exceptions import ValidationError

from daiquiri.core.adapter import DatabaseAdapter
from daiquiri.core.utils import filter_by_access_level
from daiquiri.metadata.models import Column, Function, Schema, Table

from .utils import (
    get_default_table_name,
    get_indexed_objects,
    get_max_active_jobs,
    get_quota,
    get_user_schema_name
)


def check_quota(job):
    # get the model from the instance to prevent circular inclusion
    QueryJob = type(job)

    if QueryJob.objects.get_size(job.owner) > get_quota(job.owner):
        raise ValidationError(
            {'query': [_('Quota is exceeded. Please remove some of your jobs.')]}
        )


def check_number_of_active_jobs(job):
    # get the model from the instance to prevent circular inclusion
    QueryJob = type(job)

    max_active_jobs = get_max_active_jobs(job.owner)
    if (
        max_active_jobs
        and max_active_jobs <= QueryJob.objects.get_active(job.owner).count()
    ):
        raise ValidationError(
            {
                'query': [
                    _(
                        'Too many active jobs. Please abort some of your active jobs or '
                        'wait until they are completed.'
                    )
                ]
            }
        )


def process_schema_name(user, schema_name):
    user_schema_name = get_user_schema_name(user)

    if schema_name:
        if schema_name == user_schema_name:
            return schema_name
        else:
            raise ValidationError(
                {'schema_name': [_('Only the user schema is allowed.')]}
            )
    else:
        return user_schema_name


def process_table_name(table_name):
    if table_name:
        # the tablename was checked by the TableNameValidator
        return table_name
    else:
        return get_default_table_name()


def process_query_language(user, query_language):
    # get the possible query languages for this user and create a map
    query_language_map = {}
    for item in filter_by_access_level(user, settings.QUERY_LANGUAGES):
        query_language_map['{key}-{version}'.format(**item)] = '{key}-{version}'.format(
            **item
        )
        query_language_map['{key}'.format(**item)] = '{key}-{version}'.format(**item)

    # check if a query language is set
    if query_language:
        query_language = query_language.lower()

        if query_language in query_language_map:
            return query_language_map[query_language]
        else:
            raise ValidationError(
                {'query_language': [_('This query language is not supported.')]}
            )

    else:
        # return the default query_language
        return settings.QUERY_LANGUAGES[0]['key']


def process_queue(user, queue):
    # get the possible queues for this user
    queues = filter_by_access_level(user, settings.QUERY_QUEUES)

    # check if a queue is set
    if queue:
        queue = queue.lower()

        # check if this queue is in the possible queues
        try:
            next(item for item in queues if item['key'] == queue)
        except StopIteration as e:
            raise ValidationError({'queue': [_('This queue is not supported.')]}) from e

        return queue
    else:
        # set the default queue
        return queues[0]['key']


def process_response_format(response_format):
    if response_format:
        response_format = response_format.lower()

        if response_format in [item['key'] for item in settings.QUERY_DOWNLOAD_FORMATS]:
            return response_format
        else:
            raise ValidationError(
                {'response_format': [_('This response format is not supported.')]}
            )
    else:
        # return the default response_format
        return settings.QUERY_DEFAULT_DOWNLOAD_FORMAT


def translate_query(query_language, query):
    # get the adapter
    adapter = DatabaseAdapter()

    # translate adql -> mysql string
    if query_language == 'adql-2.0':
        try:
            translator = cache.get_or_set('translator', ADQLQueryTranslator(), 3600)
            translator.set_query(query)

            if adapter.database_config['ENGINE'] == 'django.db.backends.mysql':
                return translator.to_mysql()
            elif adapter.database_config['ENGINE'] == 'django.db.backends.postgresql':
                return translator.to_postgresql()
            else:
                raise Exception('Unknown database engine')

        except QuerySyntaxError as e:
            raise ValidationError(
                {
                    'query': {
                        'messages': [
                            _('There has been an error while translating your query.')
                        ],
                        'positions': json.dumps(e.syntax_errors),
                    }
                }
            ) from e

        except QueryError as e:
            raise ValidationError(
                {
                    'query': {
                        'messages': e.messages,
                    }
                }
            ) from e

    else:
        return query


def process_query(query):
    # get the adapter
    adapter = DatabaseAdapter()

    try:
        user_defined_functions = None

        if adapter.database_config['ENGINE'] == 'django.db.backends.mysql':
            from queryparser.mysql import MySQLQueryProcessor

            processor = MySQLQueryProcessor(query)

        elif adapter.database_config['ENGINE'] == 'django.db.backends.postgresql':
            functions = Function.objects.all()

            user_defined_functions = [f.name for f in functions]

            from queryparser.postgresql import PostgreSQLQueryProcessor

            if settings.QUERY_PROCESSOR_CACHE:
                processor = cache.get_or_set(
                    'processor', PostgreSQLQueryProcessor(), 3600
                )
            else:
                processor = PostgreSQLQueryProcessor()

            # first run to replace with get_indexed_objects
            processor.set_query(query)

            processor.process_query(
                indexed_objects=get_indexed_objects(),
                replace_schema_name={
                    'TAP_SCHEMA': settings.TAP_SCHEMA,
                    'tap_schema': settings.TAP_SCHEMA,
                    'TAP_UPLOAD': settings.TAP_UPLOAD,
                    'tap_upload': settings.TAP_UPLOAD,
                },
                replace_function_names=user_defined_functions,
            )

            # second run
            processor.set_query(processor.query)
            processor.process_query(replace_function_names=user_defined_functions)

        else:
            raise Exception('Unknown database engine')

    except QuerySyntaxError as e:
        raise ValidationError(
            {
                'query': {
                    'messages': [
                        _('There has been an error while parsing your query.')
                    ],
                    'positions': json.dumps(e.syntax_errors),
                }
            }
        ) from e

    except QueryError as e:
        raise ValidationError(
            {
                'query': {
                    'messages': [
                        e.messages,
                    ],
                }
            }
        ) from e

    return processor


def process_display_columns(processor_display_columns):
    # process display_columns to expand *
    display_columns = []
    for processor_display_column, original_column in processor_display_columns:
        if processor_display_column == '*':
            schema_name, table_name, _ = original_column
            columns = (
                Column.objects.filter(table__schema__name=schema_name)
                .filter(table__name=table_name)
                .order_by('order')
            )
            if columns.exists():
                for column in columns:
                    display_columns.append(
                        (column.name, (schema_name, table_name, column.name))
                    )
            else:
                from daiquiri.query.models import QueryJob

                queryjob = QueryJob.objects.filter(
                    schema_name=schema_name, table_name=table_name
                ).first()
                if queryjob:
                    columns = queryjob.metadata['columns']
                    for column in columns:
                        display_columns.append(
                            (
                                column['name'],
                                (schema_name, table_name, column['name']),
                            )
                        )
        else:
            display_columns.append((processor_display_column, original_column))

    # check for duplicate columns in display_columns
    seen = set()
    errors = []
    for display_column_name, _ in display_columns:
        if display_column_name not in seen:
            seen.add(display_column_name)
        else:
            errors.append(
                _('Duplicate column name %(column)s') % {'column': display_column_name}
            )

    if errors:
        raise ValidationError({'query': list(errors)})

    return OrderedDict(display_columns)


def process_user_columns(job, processor_tables):
    """Process the columns of user tables"""
    columns = []

    # get type from input job itself.
    QueryJob = type(job)

    for schema_name, table_name in processor_tables:
        # check if a user table is part of the table list
        if schema_name == get_user_schema_name(job.owner):
            user_job = (
                QueryJob.objects.filter(owner=job.owner)
                .exclude(phase=QueryJob.PHASE_ARCHIVED)
                .get(table_name=table_name)
            )
            columns.extend(user_job.metadata['columns'])

    return columns


def check_permissions(user, keywords, tables, columns, functions):
    messages = []

    # removed, not sure what this was
    # check keywords against whitelist
    # for keywords in keywords:
    #     pass

    # loop over tables to check permissions on schemas/tables
    for schema_name, table_name in tables:
        # check permission on schema
        if schema_name is None:
            # schema_name must not be null, move to next table
            messages.append(_('No schema given for table %s.') % table_name)
            continue
        elif schema_name == get_user_schema_name(user):
            # all tables are allowed move to next table
            continue
        elif schema_name == settings.TAP_UPLOAD:
            # all tables are allowed move to next table
            continue
        else:
            # check permissions on the schema
            try:
                schema = Schema.objects.filter_by_access_level(user).get(
                    name=schema_name
                )
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
                Table.objects.filter_by_access_level(user).filter(schema=schema).get(
                    name=table_name
                )
            except Table.DoesNotExist:
                # table not found or not allowed, move to next table
                messages.append(_('Table %s not found.') % table_name)
                continue

    # loop over columns to check permissions or just to see if they are there,
    # but only if no error messages where appended so far
    if not messages:
        for schema_name, table_name, column_name in columns:
            if (
                schema_name in [None, get_user_schema_name(user), settings.TAP_UPLOAD]
                or table_name is None
                or column_name is None
            ):
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
                            Column.objects.filter(
                                table__schema__name=schema_name
                            ).filter(table__name=table_name).get(name=column_name)
                        except Column.DoesNotExist:
                            messages.append(_('Column %s not found.') % column_name)
                            continue
                else:
                    try:
                        schema = Schema.objects.filter_by_access_level(user).get(
                            name=schema_name
                        )
                    except Schema.DoesNotExist:
                        messages.append(_('Schema %s not found.') % schema_name)
                        continue

                    try:
                        table = (
                            Table.objects.filter_by_access_level(user)
                            .filter(schema=schema)
                            .get(name=table_name)
                        )
                    except Table.DoesNotExist:
                        messages.append(_('Table %s not found.') % table_name)
                        continue

                    if column_name == '*':
                        columns = Column.objects.filter_by_access_level(user).filter(
                            table=table
                        )
                        actual_columns = DatabaseAdapter().fetch_columns(
                            schema_name, table_name
                        )

                        column_names_set = {column.name for column in columns}
                        actual_column_names_set = {
                            column['name'] for column in actual_columns
                        }

                        if column_names_set != actual_column_names_set:
                            messages.append(
                                _('The asterisk (*) is not allowed for this table.')
                            )
                            continue

                    else:
                        try:
                            Column.objects.filter_by_access_level(user).filter(
                                table=table
                            ).get(name=column_name)
                        except Column.DoesNotExist:
                            messages.append(_('Column %s not found.') % column_name)
                            continue

    # check permissions on functions
    for function_name in functions:
        # check permission on function
        queryset = Function.objects.filter(name=function_name)

        # forbid the function if it is in metadata.functions, and the user doesn't have access.
        if queryset and not queryset.filter_by_access_level(user):
            messages.append(_('Function %s is not allowed.') % function_name)
        else:
            continue

    # return the error stack
    return list(set(messages))
