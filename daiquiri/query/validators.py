from django.core.validators import URLValidator
from django.utils.translation import gettext_lazy as _

from rest_framework.exceptions import ValidationError

from .models import QueryJob
from .utils import get_quota


class TableNameValidator(object):

    message = _('A job with this table name aready exists.')

    def set_context(self, serializer_field):
        request = serializer_field.parent.context['request']
        self.user = None if request.user.is_anonymous else request.user

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


class UploadFileValidator(object):

    message = _("The maximum file size that can be uploaded is %s.")

    def set_context(self, serializer_field):
        request = serializer_field.parent.context['request']
        self.user = None if request.user.is_anonymous else request.user

    def __call__(self, file):
        quota = get_quota(self.user, quota_settings='QUERY_UPLOAD_LIMIT')
        if file.size > quota:
            raise ValidationError({
                'file': self.message % quota
            })


class UploadParamValidator(object):

    def set_context(self, serializer_field):
        self.request = serializer_field.parent.context['request']

    def __call__(self, uploads_string):
        uploads = uploads_string.split(';')

        for upload in uploads:
            try:
                resource_name, uri = upload.split(',')
            except ValueError:
                raise ValidationError({
                    'UPLOAD': 'Field is not of the form resource_name:URI'
                })

            if uri.startswith('param:'):
                file_name = uri[len('param:'):]

                # check if alnum (+ underscore)
                if not (not file_name[0].isdigit() and all(c.isalnum() or c == '_' for c in file_name)):
                    raise ValidationError({
                        'UPLOAD': 'URI contains forbidden characters'
                    })

                # check if the file is in the body of the post request
                if file_name not in self.request.data:
                    raise ValidationError({
                        'UPLOAD': 'UPLOAD URI "%s" contains does not match uploaded file' % uri
                    })

            elif uri.startswith('http:') or uri.startswith('https:'):
                URLValidator()(uri)

            else:
                raise ValidationError('UPLOAD URI "%s" is not supported' % uri)
