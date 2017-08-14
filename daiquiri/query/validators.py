from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from rest_framework.exceptions import ValidationError

from .models import QueryJob


class TableNameValidator(object):

    message = _('A job with this table name aready exists.')

    def set_context(self, serializer_field):
        request = serializer_field.parent.context['request']
        self.user = None if request.user.is_anonymous() else request.user

        if serializer_field.parent.instance:
            self.current_table_name = serializer_field.parent.instance.table_name
        else:
            self.current_table_name = None

    def __call__(self, table_name):
        if table_name:
            if self.current_table_name and table_name == self.current_table_name:
                pass
            else:
                try:
                    QueryJob.objects.filter(owner=self.user).exclude(phase=QueryJob.PHASE_ARCHIVED).get(table_name=table_name)
                    raise ValidationError([self.message])
                except QueryJob.DoesNotExist:
                    pass

class QueryLanguageValidator(object):

    message = _('This query language is not supported.')

    def __call__(self, query_language):
        if query_language.lower() not in ['%(key)s-%(version)s' % item for item in settings.QUERY_LANGUAGES]:
            raise ValidationError([self.message])


class QueueValidator(object):

    message = _('This queue is not supported.')

    def __call__(self, queue):
        if queue.lower() not in [item['key'] for item in settings.QUERY_QUEUES]:
            raise ValidationError([self.message])


class ResponseFormatValidator(object):

    message = _('This response format is not supported.')

    def __call__(self, response_format):
        if response_format.lower() not in [item['key'] for item in settings.QUERY_DOWNLOAD_FORMATS]:
            raise ValidationError([self.message])
