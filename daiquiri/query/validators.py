from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from rest_framework.exceptions import ValidationError

from .models import QueryJob


def validate_table_name(table_name):
    if table_name:
        try:
            QueryJob.objects.get(table_name=table_name)
            raise ValidationError([_('A job with this table name aready exists.')])
        except QueryJob.DoesNotExist:
            pass


def validate_query_language(query_language):
    if query_language.lower() not in ['%(key)s-%(version)s' % item for item in settings.QUERY['query_languages']]:
        raise ValidationError([_('This query language is not supported.')])


def validate_queue(queue):
    if queue.lower() not in [item['key'] for item in settings.QUERY['queues']]:
        raise ValidationError([_('This queue is not supported.')])
