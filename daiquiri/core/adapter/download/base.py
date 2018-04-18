import logging
import csv
import six
import subprocess
import re

from django.conf import settings

from daiquiri.core.generators import generate_csv, generate_votable
from daiquiri.core.utils import get_doi_url

logger = logging.getLogger(__name__)


class BaseDownloadAdapter(object):

    def __init__(self, database_key, database_config):
        self.database_key = database_key
        self.database_config = database_config

    def generate(self, format_key, schema_name, table_name, columns, sources=None, status=None, empty=False):
        # create the final list of arguments subprocess.Popen
        self.set_args(schema_name, table_name)

        prepend = {}
        for ucd, value in settings.DOWNLOAD_PREPEND.items():
            for i, column in enumerate(columns):
                if ucd in column['ucd']:
                    prepend[i] = value

        if sources:
            links = []
            for source in sources:
                links.append({
                    'content-role': 'source',
                    'href': get_doi_url(source['doi']),
                    'name': '%(schema_name)s.%(table_name)s' % source,
                })
        else:
            links = None

        if format_key == 'csv':
            return generate_csv(self.execute(prepend=prepend))

        elif format_key == 'votable':
            return generate_votable(self.execute(prepend=prepend), columns,
                                    resource_name=schema_name, table_name=table_name,
                                    links=links, query_status=status, empty=empty)

        else:
            raise Exception('Not supported.')

    def execute(self, prepend=None):
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
                        yield [(prepend[i] + cell if i in prepend else cell) for i, cell in enumerate(row)]
                    else:
                        yield row

        except subprocess.CalledProcessError as e:
            logger.error('Command PIPE returned non-zero exit status: %s' % e)
