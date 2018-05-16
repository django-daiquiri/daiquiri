import six

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from rest_framework.exceptions import ValidationError

from daiquiri.core.utils import filter_by_access_level

from .utils import get_user_schema_name, get_default_table_name


def process_schema_name(user, schema_name):
    user_schema_name = get_user_schema_name(user)

    if schema_name:
        if schema_name == user_schema_name:
            return schema_name
        else:
            raise ValidationError({
                'schema_name': [_('Only the user schema is allowed.')]
            })
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
    for query_language in filter_by_access_level(user, settings.QUERY_LANGUAGES):
        query_language_map['%(key)s-%(version)s' % query_language] = '%(key)s-%(version)s' % query_language
        query_language_map['%(key)s' % query_language] = '%(key)s-%(version)s' % query_language

    # check if a query language is set
    if query_language:
        query_language = query_language.lower()

        if query_language in query_language_map:
            return query_language_map[query_language]
        else:
            raise ValidationError({
                'query_language': [_('This query language is not supported.')]
            })

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
            six.next((item for item in queues if item['key'] == queue))
        except StopIteration:
            raise ValidationError({
                'queue': [_('This queue is not supported.')]
            })

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
            raise ValidationError({
                'response_format': [_('This response format is not supported.')]
            })
    else:
        # return the default response_format
        return settings.QUERY_DEFAULT_DOWNLOAD_FORMAT
