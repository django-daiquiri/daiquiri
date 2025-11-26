from django.conf import settings
from django.utils.module_loading import import_string

from rest_framework.exceptions import ValidationError

from daiquiri.metadata.models import Schema, Table
from daiquiri.conesearch.adapter import ConeSearchAdapter


conesearch_adapter_class = import_string(settings.CONESEARCH_ADAPTER)

class QueryFormAdapter:
    def get_fields(self):
        raise NotImplementedError

    def get_query_language(self, data):
        raise NotImplementedError

    def get_query(self, data):
        raise NotImplementedError


class ConeSearchQueryFormAdapter(conesearch_adapter_class, QueryFormAdapter):

    def get_tables(self):
        resources = self.get_resources().values()
        return [{'id':t, 'value': t, 'label': t} for
                t in dict.fromkeys(f"{v['schema_name']}.{v['table_name']}" for v in resources)]

    def get_fields(self):
        tables_list = self.get_tables()
        defaults = settings.CONESEARCH_DEFAULTS
        return [
            {
                'key': 'table',
                'type': 'select',
                'label': 'Select a Table',
                'help': 'Choose a Table',
                'width': 12,
                'options': tables_list,
                'default_value': tables_list[0]['value']
            },
            {
                'key': 'ra',
                'type': 'number',
                'label': 'RA',
                'help': 'Right ascension in degrees (decimal form)',
                'default_value': defaults['RA'],
                'width': 4,
            },
            {
                'key': 'dec',
                'type': 'number',
                'label': 'DEC',
                'help': 'Declination in degrees (decimal form)',
                'default_value': defaults['DEC'],
                'width': 4,
            },
            {
                'key': 'radius',
                'type': 'number',
                'label': 'Radius',
                'help': 'Radius in degrees',
                'default_value': defaults['SR'],
                'width': 4,
            },
        ]

    def get_columns(self, schema_name, table_name):

        try:
            schema = Schema.objects.get(name=schema_name)
        except Schema.DoesNotExist:
            raise ValidationError({"query": {"messages": [f"Schema '{schema_name}' does not exist"]}})

        try:
            table = Table.objects.filter(schema=schema).get(name=table_name)
        except Table.DoesNotExist:
            raise ValidationError({"query": {"messages": [f"Table '{table_name}' does not exist"]}})

        columns = list(table.columns.filter(principal=True).values_list('name', flat=True))
        return columns

    def get_query(self, data):
        resources = self.get_resources()
        schema_name = resources[data['table']]['schema_name']
        table_name = resources[data['table']]['table_name']
        columns = self.get_columns(schema_name, table_name)

        return self.sql_pattern.format(schema=schema_name,
                                        table=table_name,
                                        columns=', '.join(columns),
                                        RA=data['ra'], DEC=data['dec'], SR=data['radius']).strip()