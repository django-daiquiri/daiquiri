#!/usr/bin/env python
import os
import sys

import django
from django.conf import settings
from django.test.utils import get_runner

daiquiri_apps = [
    'daiquiri_auth',
    'daiquiri_contact',
    'daiquiri_core',
    'daiquiri_meetings',
    'daiquiri_query',
    'daiquiri_serve',
    'daiquiri_uws',
]

if __name__ == "__main__":
    os.environ['DJANGO_SETTINGS_MODULE'] = 'testing.settings'
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=1)
    failures = test_runner.run_tests(daiquiri_apps)
    sys.exit(bool(failures))
