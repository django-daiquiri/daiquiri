import logging
import csv
import subprocess
import re

from django.apps import apps
from django.conf import settings

from daiquiri.core.generators import generate_csv, generate_votable, generate_fits
from daiquiri.core.utils import get_doi_url

logger = logging.getLogger(__name__)


class BaseDownloadAdapter(object):

    def __init__(self, database_key, database_config):
        self.database_key = database_key
        self.database_config = database_config

    def generate(self, format_key, columns, sources=[], schema_name=None, table_name=None, nrows=None,
                 query_status=None, query=None, query_language=None):
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
                                        table=self.get_table_name(schema_name, table_name),
                                        infos=self.get_infos(query_status, query, query_language, sources),
                                        links=self.get_links(sources),
                                        services=self.get_services(),
                                        empty=(nrows==0))

            elif format_key == 'fits':
                return generate_fits(self.generate_rows(prepend=prepend), columns, nrows,
                                     table_name=self.get_table_name(schema_name, table_name))

            else:
                raise Exception('Not supported.')

    def generate_dump(self):
        # log the arguments
        logger.debug('execute "%s"' % ' '.join(self.args))

        # excecute the subprocess
        try:
            process = subprocess.Popen(self.args, stdout=subprocess.PIPE)

            for line in process.stdout:
                if not line.startswith((b'\n', b'\r\n', b'--', b'SET', b'/*!')):
                    yield line.decode()

        except subprocess.CalledProcessError as e:
            logger.error('Command PIPE returned non-zero exit status: %s' % e)

    def generate_rows(self, prepend=None):
        # log the arguments
        logger.debug('execute "%s"' % ' '.join(self.args))

        # excecute the subprocess
        try:
            process = subprocess.Popen(self.args, stdout=subprocess.PIPE)

            for line in process.stdout:
                insert_pattern = re.compile('^INSERT INTO .*? VALUES \\((.*?)\\);')
                insert_result = insert_pattern.match(line.decode())
                if insert_result:
                    line = insert_result.group(1)
                    reader = csv.reader([line], quotechar="'", skipinitialspace=True)
                    row = next(reader)

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
                    ('meta.file' in column_ucd or
                     'meta.note' in column_ucd or
                     'meta.image' in column_ucd):
                prepend[i] = settings.FILES_BASE_URL

        return prepend

    def get_table_name(self, schema_name, table_name):
        return '%(schema_name)s.%(table_name)s' % {
            'schema_name': schema_name,
            'table_name': table_name
        }

    def get_infos(self, query_status, query, query_language, sources):
        infos = [
            ('QUERY_STATUS', query_status),
            ('QUERY', query),
            ('QUERY_LANGUAGE', query_language)
        ]

        for source in sources:
            infos.append(('SOURCE', '%(schema_name)s.%(table_name)s' % source))

        return infos

    def get_links(self, sources):
        return [(
            '%(schema_name)s.%(table_name)s' % source,
            'doc',
            get_doi_url(source['doi']) if source['doi'] else source['url']
        ) for source in sources]

    def get_services(self):
        services = []
        if apps.is_installed('daiquiri.datalink'):
            from daiquiri.datalink.vo import get_service
            services.append(get_service())
        return services
