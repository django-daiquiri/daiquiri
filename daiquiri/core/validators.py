import re

from django.utils.translation import gettext_lazy as _

from rest_framework.exceptions import ValidationError


class DatabaseObjectNameValidator:

    message_allowed_chars = _(
        'Please only use letters, numbers, hyphens or underscores.'
    )

    def __call__(self, name, serializer_field=None):
        self.validate_name(name)

    def validate_name(self, name):
        if bool(re.search(r'^[0-9a-zA-Z_\-]+$', name)) is False:
            raise ValidationError([self.message_allowed_chars])