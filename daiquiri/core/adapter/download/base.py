import logging
import csv
import six
import subprocess
import re

from django.conf import settings

from daiquiri.core.generators import generate_csv, generate_votable, generate_fits

logger = logging.getLogger(__name__)


class BaseDownloadAdapter(object):

    def __init__(self, database_key, database_config):
        self.database_key = database_key
        self.database_config = database_config

    def generate(self, format_key, schema_name, table_name, columns, sources=None, status=None, nrows=None):
        # create the final list of arguments subprocess.Popen
        if format_key == 'sql':
            # create the final list of arguments subprocess.Popen
            self.set_args(schema_name, table_name)

            return self.generate_dump()
        else:
            # create the final list of arguments subprocess.Popen
            self.set_args(schema_name, table_name, data_only=True)

            # prepend strings with settings.FILES_BASE_PATH if they refer to files
            prepend = self.get_prepend(columns)

            if format_key == 'csv':
                return generate_csv(self.generate_rows(prepend=prepend), columns)

            elif format_key == 'votable':
                return generate_votable(self.generate_rows(prepend=prepend), columns,
                                        resource_name=schema_name, table_name=table_name,
                                        sources=sources, query_status=status, empty=(nrows==0))

            elif format_key == 'fits':
                return generate_fits(self.generate_rows(prepend=prepend), columns,
                                     nrows=nrows, table_name=table_name)

            else:
                raise Exception('Not supported.')

    def generate_dump(self):
        # log the arguments
        logger.debug('execute "%s"' % ' '.join(self.args))

        # excecute the subprocess
        try:
            process = subprocess.Popen(self.args, stdout=subprocess.PIPE)

            for line in process.stdout:
                if not line.startswith(('\n', '\r\n', '--', 'SET', '/*!')):
                    yield line

        except subprocess.CalledProcessError as e:
            logger.error('Command PIPE returned non-zero exit status: %s' % e)

    def generate_rows(self, prepend=None):
        # log the arguments
        logger.debug('execute "%s"' % ' '.join(self.args))

        # excecute the subprocess
        try:
            process = subprocess.Popen(self.args, stdout=subprocess.PIPE)

            for line in process.stdout:
                insert_pattern = re.compile('^INSERT INTO .*? VALUES \((.*?)\);')
                insert_result = insert_pattern.match(line.decode())
                if insert_result:
                    line = insert_result.group(1)
                    reader = csv.reader([line], quotechar="'", skipinitialspace=True)
                    row = six.next(reader)

                    if prepend:
                        yield [(prepend[i] + cell if (i in prepend and cell != 'NULL') else cell) for i, cell in enumerate(row)]
                    else:
                        yield row

        except subprocess.CalledProcessError as e:
            logger.error('Command PIPE returned non-zero exit status: %s' % e)

    def get_prepend(self, columns):
        if not settings.FILES_BASE_URL:
            return {}

        # prepend strings with settings.FILES_BASE_PATH if they refer to files
        prepend = {}

        for i, column in enumerate(columns):
            column_ucd = column.get('ucd')
            if column_ucd and 'meta.ref' in column_ucd and \
                ('meta.file' in column_ucd or 'meta.note' in column_ucd or 'meta.image' in column_ucd):
                    prepend[i] = settings.FILES_BASE_URL

        return prepend
