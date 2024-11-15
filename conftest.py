import os

import pytest

from django.conf import settings
from django.contrib.admin.utils import flatten
from django.core.management import call_command

from daiquiri.core.constants import GROUPS
from daiquiri.core.utils import setup_group


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):  # noqa: PT004
    from django.test import TestCase
    TestCase.multi_db = True
    TestCase.databases = ('default', 'data', 'tap', 'oai')

    with django_db_blocker.unblock():
        fixtures = flatten([os.listdir(fixture_dir) for fixture_dir in settings.FIXTURE_DIRS])

        call_command('loaddata', *fixtures)
        for name in GROUPS:
            group, created = setup_group(name)
