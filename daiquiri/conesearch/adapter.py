from django.conf import settings
from django.http import FileResponse
from django.utils.translation import gettext_lazy as _

from rest_framework.exceptions import NotFound, ValidationError

from daiquiri.core.adapter import DatabaseAdapter
from daiquiri.core.adapter.stream import BaseServiceAdapter
from daiquiri.core.generators import generate_votable
from daiquiri.core.utils import import_class, make_query_dict_upper_case


def ConeSearchAdapter():
    return import_class(settings.CONESEARCH_ADAPTER)()


class BaseConeSearchAdapter(BaseServiceAdapter):

    keys = ['RA', 'DEC', 'SR']

    ranges = {
        'RA': {
            'min': 0,
            'max': 360
        },
        'DEC': {
            'min': -90,
            'max': 90
        },
        'SR': {
            'min': 0,
            'max': 10
        }
    }

    defaults = {
        'RA': 20,
        'DEC': 20,
        'SR': 10,
    }

    columns = [
        {
            'name': 'id',
            'ucd': 'meta.id; meta.main',
            'datatype': 'char',
            'arraysize': '*'
        },
        {
            'name': 'RA',
            'ucd': 'pos.eq.ra; meta.main',
            'datatype': 'double'
        },
        {
            'name': 'DEC',
            'ucd': 'pos.eq.dec; meta.main',
            'datatype': 'double'
        }
    ]

    max_records = 10000

    def get_resources(self):
        raise NotImplementedError()

    def clean(self, request, resource):
        raise NotImplementedError()

    def clean_args(self, data, errors):
        # parse RA, DEC, and SR arguments
        self.args = {}
        for key in ['RA', 'DEC', 'SR']:
            try:
                value = float(data[key])

                if self.ranges[key]['min'] <= value <= self.ranges[key]['max']:
                    self.args[key] = value
                else:
                    errors[key] = [_('This value must be between {min:g} and {max:g}.').format(**self.ranges[key])]

            except KeyError:
                errors[key] = [_('This field may not be blank.')]

            except ValueError:
                errors[key] = [_('This field must be a float.')]

    def stream(self):
        return FileResponse(
            generate_votable(DatabaseAdapter().fetchall(self.sql, self.args), self.columns),
            content_type='application/xml'
        )


class SimpleConeSearchAdapter(BaseConeSearchAdapter):

    def get_resources(self):
        return [settings.CONESEARCH_TABLE]

    def clean(self, request, resource):
        if resource not in self.get_resources():
            raise NotFound()

        adapter = DatabaseAdapter()

        self.sql = '''
SELECT {id_field}, {ra_field}, {dec_field}
FROM {schema}.{table}
WHERE
    {ra_field} BETWEEN (%(RA)s - 0.5 * %(SR)s) AND (%(RA)s + 0.5 * %(SR)s)
AND
    {dec_field} BETWEEN (%(DEC)s - 0.5 * %(SR)s) AND (%(DEC)s + 0.5 * %(SR)s)
LIMIT {limit}
'''.format(
            id_field=adapter.escape_identifier('id'),
            ra_field=adapter.escape_identifier('ra'),
            dec_field=adapter.escape_identifier('dec'),
            schema=settings.CONESEARCH_SCHEMA,
            table=settings.CONESEARCH_TABLE,
            limit=self.max_records,
        )

        self.args, errors = self.parse_query_dict(request)

        if errors:
            raise ValidationError(errors)


class TableConeSearchAdapter(BaseConeSearchAdapter):

    def clean(self, request, resource):
        from daiquiri.metadata.models import Schema, Table

        resources = self.get_resources()

        if resource not in resources:
            raise NotFound

        schema_name = resources[resource]['schema_name']
        table_name = resources[resource]['table_name']

        data = make_query_dict_upper_case(request.GET)
        errors = {}

        # check if the user is allowed to access the schema
        try:
            schema = Schema.objects.filter_by_access_level(request.user).get(name=schema_name)
        except Schema.DoesNotExist as e:
            raise NotFound from e

        # check if the user is allowed to access the table
        try:
            table = Table.objects.filter_by_access_level(request.user).filter(schema=schema).get(name=table_name)
        except Table.DoesNotExist as e:
            raise NotFound from e

        # fetch the columns according to the verbosity
        verb = data.get('VERB', '2')

        if verb == '1':
            self.columns = table.columns.filter(name__in=resources[resource]['column_names']).values()
        elif verb == '2':
            self.columns = table.columns.filter(principal=True).values()
        elif verb == '3':
            self.columns = table.columns.values()
        else:
            errors['VERB'] = [_('This field must be 1, 2, or 3.')]

        # construct sql query
        adapter = DatabaseAdapter()
        escaped_column_names = [adapter.escape_identifier(column['name']) for column in self.columns]
        self.sql = self.sql_pattern % {
            'schema': adapter.escape_identifier(schema_name),
            'table': adapter.escape_identifier(table_name),
            'columns': ', '.join(escaped_column_names)
        }

        # parse RA, DEC, and SR arguments
        self.args = {}
        for key in ['RA', 'DEC', 'SR']:
            try:
                value = float(data[key])

                if self.ranges[key]['min'] <= value <= self.ranges[key]['max']:
                    self.args[key] = value
                else:
                    errors[key] = [_('This value must be between {min:g} and {max:g}.').format(**self.ranges[key])]

            except KeyError:
                errors[key] = [_('This field may not be blank.')]

            except ValueError:
                errors[key] = [_('This field must be a float.')]

        if errors:
            raise ValidationError(errors)
