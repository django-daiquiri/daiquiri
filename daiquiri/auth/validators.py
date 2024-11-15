import re

from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _

'''
The validator should be included by adding:

    ACCOUNT_USERNAME_VALIDATORS = 'daiquiri.auth.validators.username_validators'

to settings/base.py.
'''

@deconstructible
class DaiquiriUsernameValidator(validators.RegexValidator):
    '''
    This is almost identical to https://github.com/django/django/blob/main/django/core/validators.py
    '''
    regex = r'^[a-z0-9_]+\Z'
    message = _(
        'Enter a valid username. This value may contain only English lowercase letters, '
        'numbers, and underscores.'
    )
    flags = re.ASCII


username_validators = [DaiquiriUsernameValidator()]
