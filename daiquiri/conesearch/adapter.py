from django.conf import settings
from django.http import FileResponse
from django.utils.translation import gettext_lazy as _

from rest_framework.exceptions import NotFound, ValidationError

from queryparser.adql import ADQLQueryTranslator

from daiquiri.core.adapter import DatabaseAdapter
from daiquiri.core.adapter.stream import BaseServiceAdapter
from daiquiri.core.generators import generate_votable
from daiquiri.core.utils import import_class, make_query_dict_upper_case
from daiquiri.metadata.models import Schema, Table


def ConeSearchAdapter():
    return import_class(settings.CONESEARCH_ADAPTER)()


class BaseConeSearchAdapter(BaseServiceAdapter):
    keys = ['RA', 'DEC', 'SR']

    sql_pattern = """
SELECT {columns}
FROM {schema}.{table}
WHERE 1=CONTAINS(POINT(ra, dec), CIRCLE(POINT({RA}, {DEC}), {SR}))
"""
    defaults = settings.CONESEARCH_DEFAULTS
    ranges = settings.CONESEARCH_RANGES
    max_records = settings.CONESEARCH_MAX_RECORDS

    def get_resources(self):
        return settings.CONESEARCH_RESOURCES

    def get_query_language(self):
        return 'ADQL'  #'postgresql-16.2'

    def clean(self, request, resource):
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
            table = (
                Table.objects.filter_by_access_level(request.user)
                .filter(schema=schema)
                .get(name=table_name)
            )
        except Table.DoesNotExist as e:
            raise NotFound from e

        # fetch the columns according to the verbosity
        verb = data.get('VERB', '2')

        if verb == '1':
            self.columns = table.columns.filter(
                name__in=resources[resource]['column_names']
            ).values()
        elif verb == '2':
            self.columns = table.columns.filter(principal=True).values()
            if not self.columns:
                raise NotFound(_('There are no principal columns'))
        elif verb == '3':
            self.columns = table.columns.values()
        else:
            errors['VERB'] = [_('This field must be 1, 2, or 3.')]

        # parse RA, DEC, and SR arguments
        self.clean_args(data, errors)

        # construct sql query
        adapter = DatabaseAdapter()
        escaped_column_names = [
            adapter.escape_identifier(column['name']) for column in self.columns
        ]
        self.sql = self.sql_pattern.format(
            schema=adapter.escape_identifier(schema_name),
            table=adapter.escape_identifier(table_name),
            columns=', '.join(escaped_column_names),
            escaped_column_names=escaped_column_names,
            **self.args,
        ).strip()

        if 'ADQL' in self.get_query_language():
            self.sql = ADQLQueryTranslator(self.sql)
            self.sql = self.sql.to_postgresql()

        if errors:
            raise ValidationError(errors)

    def clean_args(self, data, errors):
        self.args = {}
        for key in ['RA', 'DEC', 'SR']:
            try:
                value = float(data[key])

                if self.ranges[key]['min'] <= value <= self.ranges[key]['max']:
                    self.args[key] = value
                else:
                    errors[key] = [
                        _('This value must be between {min:g} and {max:g}.').format(
                            **self.ranges[key]
                        )
                    ]

            except KeyError:
                errors[key] = [_('This field may not be blank.')]

            except ValueError:
                errors[key] = [_('This field must be a float.')]

    def stream(self):
        return FileResponse(
            generate_votable(DatabaseAdapter().fetchall(self.sql, self.args), self.columns),
            content_type='application/xml',
        )
