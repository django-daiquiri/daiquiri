#!/usr/bin/env python
import argparse
import subprocess

parser = argparse.ArgumentParser(description='Perform tests using covarage.')
parser.add_argument('--html', action='store_true', default=False, help='Create HTML coverage report')

args = parser.parse_args()
try:
    subprocess.call(['coverage', 'run', 'runtests.py'])
    subprocess.call(['coverage', 'report'])
    if args.html:
        subprocess.call(['coverage', 'html'])
except OSError:
    raise Exception('coverage is not installed')
