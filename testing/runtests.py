#!/usr/bin/env python
import argparse
import os
import sys

import django
from django.conf import settings
from django.test.utils import get_runner

test_labels = [
    'daiquiri.auth',
    'daiquiri.core'
]


def main():
    parser = argparse.ArgumentParser(description='Run the tests for Daiquiri.')
    parser.add_argument('-k', '--keepdb', action='store_true', help='Preserves the test DB between runs.')

    args = parser.parse_args()

    testing_path = os.path.dirname(__file__)
    daiquiri_path = os.path.dirname(testing_path)

    sys.path.append(daiquiri_path)
    os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

    django.setup()
    TestRunner = get_runner(settings)
    failures = TestRunner(verbosity=1, keepdb=args.keepdb).run_tests(test_labels)
    sys.exit(bool(failures))


if __name__ == "__main__":
    main()
