import csv
import logging
import re
import subprocess
from urllib.parse import urljoin

from django.apps import apps
from django.conf import settings

from daiquiri.core.adapter import DatabaseAdapter
from daiquiri.core.generators import (
    generate_csv,
    generate_fits,
    generate_parquet,
    generate_votable,
)
from daiquiri.core.pgsphere import (
    ADQL_GEOMETRIES,
    PGSPHERE_TYPES,
    process_result_columns,
    process_result_row,
)
from daiquiri.core.utils import get_doi_url, is_adql

logger = logging.getLogger(__name__)


def _report_rows(rows, on_row_count):
    count = 0
    for row in rows:
        yield row
        # The consumer has finished this row when iteration resumes.
        count += 1
        if count % 1000 == 0:
            on_row_count(count)
    if count % 1000:
        on_row_count(count)


class BaseDownloadAdapter:
    def __init__(self, database_key, database_config):
        self.database_key = database_key
        self.database_config = database_config

    def generate(
        self,
        format_key,
        columns,
        sources=[],
        schema_name=None,
        table_name=None,
        nrows=None,
        query_status=None,
        query=None,
        query_language=None,
        on_row_count=None,
        on_error=None,
    ):
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
            native_columns = columns
            columns = process_result_columns(native_columns, query_language)
            rows = self.generate_rows(prepend=prepend)
            if is_adql(query_language) and any(
                column.get('datatype') in ADQL_GEOMETRIES for column in native_columns
            ):
                rows = (process_result_row(row, native_columns, query_language) for row in rows)
            if on_row_count:
                rows = _report_rows(rows, on_row_count)

            if format_key == 'csv':
                return generate_csv(rows, columns)

            elif format_key == 'votable':
                services = self.get_services_for_fields(columns)
                return generate_votable(
                    rows,
                    fields=columns,
                    table=self.get_table_name(schema_name, table_name),
                    infos=self.get_infos(query_status, query, query_language, sources),
                    links=self.get_links(sources),
                    services=services,
                    empty=(nrows == 0),
                    on_error=on_error,
                )

            elif format_key == 'fits':
                schema_table_name = self.get_table_name(schema_name, table_name)
                fits_field_widths = self.get_arraysizes_for_fits(
                    native_columns, schema_name, table_name, query_language
                )

                return generate_fits(
                    rows,
                    fields=columns,
                    nrows=nrows,
                    table_name=schema_table_name,
                    array_infos=fits_field_widths,
                )

            elif format_key == 'parquet':
                services = self.get_services_for_fields(columns)
                votable_meta = generate_votable(
                    rows,
                    fields=columns,
                    table=self.get_table_name(schema_name, table_name),
                    infos=self.get_infos(query_status, query, query_language, sources),
                    links=self.get_links(sources),
                    services=services,
                    empty=True,
                )
                votable_meta_str = ''
                for line in votable_meta:
                    votable_meta_str += line

                return generate_parquet(
                    schema_name=schema_name,
                    table_name=table_name,
                    fields=native_columns,
                    metadata=votable_meta_str,
                    database_config=self.database_config,
                    query_language=query_language,
                    on_row_count=on_row_count,
                )

            else:
                raise Exception('Not supported.')

    def generate_dump(self):
        # log the arguments
        logger.debug('execute "%s"', ' '.join(self.args))

        # execute the subprocess
        try:
            process = subprocess.Popen(self.args, stdout=subprocess.PIPE)

            for line in process.stdout:
                if not line.startswith((b'\n', b'\r\n', b'--', b'SET', b'/*!')):
                    yield line.decode()

        except subprocess.CalledProcessError as e:
            logger.error('Command PIPE returned non-zero exit status: %s', e)

    def generate_rows(self, prepend=None):
        # log the arguments
        logger.debug('execute "%s"', ' '.join(self.args))

        # execute the subprocess
        process = subprocess.Popen(self.args, stdout=subprocess.PIPE)
        try:
            insert_pattern = re.compile(r'^INSERT INTO .*? VALUES \((.*?)\);\s*$')
            for line in process.stdout:
                insert_result = insert_pattern.match(line.decode())
                if insert_result:
                    line = insert_result.group(1)
                    reader = csv.reader([line], quotechar="'", skipinitialspace=True)
                    row = next(reader)
                    if prepend:
                        yield from self.prepend_row_values(row, prepend)
                    else:
                        yield row

        except subprocess.CalledProcessError as e:
            logger.error('Command PIPE returned non-zero exit status: %s', e)
        finally:
            process.stdout.close()
            _ = process.wait()

    def get_prepend(self, columns):
        """Returns a dict with prefixes to prepend FILES_BASE_URL to file references in the data"""
        if not settings.FILES_BASE_URL:
            return {}

        # prepend strings with settings.FILES_BASE_PATH if they refer to files
        prepend = {}

        for i, column in enumerate(columns):
            column_ucd = column.get('ucd')
            if (
                column_ucd
                and 'meta.ref' in column_ucd
                and (
                    'meta.file' in column_ucd
                    or 'meta.note' in column_ucd
                    or 'meta.image' in column_ucd
                )
            ):
                prepend[i] = settings.FILES_BASE_URL

        return prepend

    def prepend_row_values(self, row, prepend):
        """Prepend values in rows according to the prepend dict.
        Used to prepend settings.FILES_BASE_URL to file references in the data,
        based on the column UCDs.
        """
        if prepend:
            yield [
                (
                    urljoin(prepend[i], cell)
                    if (i in prepend and cell not in ('NULL', None))
                    else cell
                )
                for i, cell in enumerate(row)
            ]
        else:
            yield row

    def get_table_name(self, schema_name, table_name):
        return f'{schema_name}.{table_name}'

    def get_infos(self, query_status, query, query_language, sources):
        infos = [
            ('QUERY_STATUS', query_status),
            ('QUERY', query),
            ('QUERY_LANGUAGE', query_language),
        ]

        for source in sources:
            infos.append(('SOURCE', '{schema_name}.{table_name}'.format(**source)))

        return infos

    def get_links(self, sources):
        return [
            (
                '{schema_name}.{table_name}'.format(**source),
                'doc',
                get_doi_url(source['doi']) if source['doi'] else source['url'],
            )
            for source in sources
        ]

    def get_services(self):
        services = []
        if apps.is_installed('daiquiri.datalink'):
            from daiquiri.datalink.vo import get_service

            services.append(get_service())
        return services

    def get_services_for_fields(self, fields):
        services = self.get_services()
        if apps.is_installed('daiquiri.datalink'):
            from daiquiri.datalink.vo import get_service, get_service_descriptors

            field_services = get_service_descriptors(fields)
            if field_services:
                legacy_service = get_service()
                services = [service for service in services if service != legacy_service]
            for service in field_services:
                if service not in services:
                    services.append(service)
        return services

    def get_arraysizes_for_fits(
        self, columns: list, schema_name: str, table_name: str, query_language=None
    ):
        """Return fixed text widths needed for native pgSphere FITS fields."""
        field_widths = {}
        db = DatabaseAdapter()
        for c in columns:
            datatype = c['datatype']
            if datatype in PGSPHERE_TYPES:
                geometry = ADQL_GEOMETRIES.get(datatype) if is_adql(query_language) else None
                if geometry:
                    continue
                column = db.escape_identifier(c['name'])
                table = f'{db.escape_identifier(schema_name)}.{db.escape_identifier(table_name)}'
                # Native pgSphere values are written as fixed-width text.
                length = f'octet_length({column}::text)'
                field_widths[c['name']] = db.fetchone(f'SELECT MAX({length}) FROM {table}')[0] or 1

        return field_widths
