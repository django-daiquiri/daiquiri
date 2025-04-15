import re

from django.core.validators import URLValidator
from django.utils.translation import gettext_lazy as _

from rest_framework.exceptions import ValidationError

from daiquiri.core.utils import bytes2human

from .models import QueryJob
from .utils import get_quota


class TableNameValidator:

    requires_context = True

    message = _('A job with this table name already exists.')
    message_allowed_chars = _(
        'Please only use letters, numbers, hyphens or underscores.'
    )

    def __call__(self, table_name, serializer_field):
        request = serializer_field.parent.context['request']
        user = None if request.user.is_anonymous else request.user

        if serializer_field.parent.instance:
            current_table_name = serializer_field.parent.instance.table_name
        else:
            current_table_name = None

        if bool(re.search(r'^[0-9a-zA-Z_\-]+$', table_name)) is False:
            raise ValidationError([self.message_allowed_chars])
        if table_name:
            if current_table_name and table_name == current_table_name:
                pass
            else:
                try:
                    QueryJob.objects.filter(owner=user).exclude(phase=QueryJob.PHASE_ARCHIVED).get(table_name=table_name)
                    raise ValidationError([self.message])
                except QueryJob.DoesNotExist:
                    pass


class UploadFileValidator:

    requires_context = True

    message = _("The maximum file size that can be uploaded is %s.")

    def __call__(self, file, serializer_field):
        request = serializer_field.parent.context['request']
        user = None if request.user.is_anonymous else request.user

        quota = get_quota(user, quota_settings='QUERY_UPLOAD_LIMIT')
        if file.size > quota:
            raise ValidationError([self.message % bytes2human(quota)])


class UploadParamValidator:

    requires_context = True

    def __call__(self, uploads_string, serializer_field):
        request = serializer_field.parent.context['request']

        uploads = uploads_string.split(';')

        for upload in uploads:
            try:
                resource_name, uri = upload.split(',')
            except ValueError as e:
                raise ValidationError({
                    'UPLOAD': 'Field is not of the form resource_name:URI'
                }) from e

            if uri.startswith('param:'):
                file_name = uri[len('param:'):]

                # check if alnum (+ underscore)
                if not (not file_name[0].isdigit() and all(c.isalnum() or c == '_' for c in file_name)):
                    raise ValidationError({
                        'UPLOAD': 'URI contains forbidden characters'
                    })

                # check if the file is in the body of the post request
                if file_name not in request.data:
                    raise ValidationError({
                        'UPLOAD': f'UPLOAD URI "{uri}" contains does not match uploaded file'
                    })

            elif uri.startswith('http:') or uri.startswith('https:'):
                URLValidator()(uri)

            else:
                raise ValidationError(f'UPLOAD URI "{uri}" is not supported')
