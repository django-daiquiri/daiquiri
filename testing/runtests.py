#!/usr/bin/env python
import argparse
import os
import sys

import django
from django.conf import settings
from django.test.utils import get_runner


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('test_label', nargs='*', help='Module paths to test; can be modulename, modulename.TestCase or modulename.TestCase.test_method')
    parser.add_argument('-k', '--keepdb', action='store_true', help='Preserves the test DB between runs.')
    parser.add_argument('-v', '--verbosity', type=int, default=1, help='Verbosity level; 0=minimal output, 1=normal output, 2=verbose output, 3=very verbose output')
    args = parser.parse_args()

    os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
    django.setup()

    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=args.verbosity, keepdb=args.keepdb)
    failures = test_runner.run_tests(args.test_label)
    sys.exit(bool(failures))

if __name__ == "__main__":
    main()
