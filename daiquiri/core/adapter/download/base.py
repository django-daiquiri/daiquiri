import logging
import csv
import six
import subprocess
import re
import string

from daiquiri.core.generators import generate_csv, generate_votable

logger = logging.getLogger(__name__)


class DownloadAdapter(object):

    def __init__(self, database_key, database_config):
        self.database_key = database_key
        self.database_config = database_config

    def generate(self, format_key, schema_name, table_name, metadata, status=None, empty=False):
        # create the final list of arguments subprocess.Popen
        self.set_args(schema_name, table_name)

        if format_key == 'csv':
            return generate_csv(self.execute())

        elif format_key == 'votable':
            return generate_votable(self.execute(), metadata['columns'],
                                    resource_name=schema_name, table_name=table_name,
                                    query_status=status, empty=empty)

        else:
            raise Exception('Not supported.')

    def execute(self):
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
                    yield map(string.strip, row)

        except subprocess.CalledProcessError as e:
            logger.error('Command PIPE returned non-zero exit status: %s' % e)
