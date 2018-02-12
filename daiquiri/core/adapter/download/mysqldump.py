import logging
import base64
import csv
import io
import re
import six
import struct
import subprocess
import sys

from bitstring import BitArray

from .base import DownloadAdapter

logger = logging.getLogger(__name__)

class MysqldumpAdapter(DownloadAdapter):

    insert_pattern = re.compile('^INSERT INTO .*? VALUES \((.*?)\);')

    FORMATS = {
        'char': 'c',
        'unsignedByte': 'B',
        'short': 'h',
        'int': 'i',
        'long': 'q',
        'float': 'f',
        'double': 'd'
    }

    NULL_VALUES = {
        'char': '',
        'unsignedByte': 255,
        'short': 32767,
        'int': 2147483647,
        'long': 9223372036854775807,
        'float': float('nan'),
        'double': float('nan')
    }

    def __init__(self, database_key, database_config):
        self.args = ['mysqldump', '--compact', '--skip-extended-insert']

        if 'USER' in database_config and database_config['USER']:
            self.args.append('--user=%(USER)s' % database_config)

        if 'PASSWORD' in database_config and database_config['PASSWORD']:
            self.args.append('--password=%(PASSWORD)s' % database_config)

        if 'HOST' in database_config and database_config['HOST']:
            self.args.append('--host=%(HOST)s' % database_config)

        if 'PORT' in database_config and database_config['PORT']:
            self.args.append('--port=%(PORT)s' % database_config)

    def generate(self, format_key, database_name, table_name, metadata, status=None, empty=False):

        if format_key == 'csv':
            return self.generate_csv(database_name, table_name)

        elif format_key == 'votable':
            return self.generate_votable('TABLEDATA', database_name, table_name, metadata, status, empty)

        elif format_key == 'votable-binary':
            return self.generate_votable('BINARY', database_name, table_name, metadata, status, empty)

        elif format_key == 'votable-binary2':
            return self.generate_votable('BINARY2', database_name, table_name, metadata, status, empty)

        else:
            raise Exception('Not supported.')

    def _set_args(self, database_name, table_name):
        # append 'database_name table_name'
        self.args.append(database_name)
        self.args.append(table_name)
        return self.args

