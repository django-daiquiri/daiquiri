#!/usr/bin/env python
import os
import sys

import django
from django.conf import settings
from django.test.utils import get_runner

daiquiri_apps = [
    'daiquiri.auth',
    'daiquiri.contact',
    'daiquiri.core',
    'daiquiri.dali',
    'daiquiri.jobs',
    'daiquiri.meetings',
    'daiquiri.metadata',
    'daiquiri.query',
    'daiquiri.serve',
    'daiquiri.tap',
    'daiquiri.uws'
]

if __name__ == "__main__":
    testing_path = os.path.dirname(__file__)
    daiquiri_path = os.path.dirname(testing_path)


    sys.path.append(daiquiri_path)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=1)
    failures = test_runner.run_tests(daiquiri_apps)
    sys.exit(bool(failures))
