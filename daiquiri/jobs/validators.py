from rest_framework.exceptions import ValidationError


class UploadValidator(object):

    def set_context(self, serializer_field):
        self.request = serializer_field.parent.context['request']

    def __call__(self, upload):

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
                    'UPLOAD': 'UPLOAD URI contains does not match uploaded file'
                })

        else:
            raise ValidationError('UPLOAD URI is not supported')
