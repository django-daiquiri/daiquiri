from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from rest_framework.exceptions import ValidationError


def process_table_name(table_name):
    pass


def process_query_language(query_language):
    if query_language:
        query_language = query_language.lower()

        query_languages = {}
        for item in settings.QUERY_LANGUAGES:
            query_languages['%(key)s-%(version)s' % item] = '%(key)s-%(version)s' % item
            query_languages['%(key)s' % item] = '%(key)s-%(version)s' % item

        if query_language in query_languages:
            return query_languages[query_language]
        else:
            raise ValidationError({
                'query_language': [_('This query language is not supported.')]
            })
    else:
        # return the default query_language
        return settings.QUERY_LANGUAGES[0]['key']


def process_queue(queue):
    if queue:
        queue = queue.lower()

        if queue in [item['key'] for item in settings.QUERY_QUEUES]:
            return queue
        else:
            raise ValidationError({
                'queue': [_('This queue is not supported.')]
            })
    else:
        # return the default queue
        return settings.QUERY_QUEUES[0]['key']


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
