from django.conf import settings
from django.utils.module_loading import import_string

from rest_framework.exceptions import NotFound, ValidationError

from daiquiri.metadata.models import Schema, Table


ConeSearchBaseClass = import_string(settings.CONESEARCH_ADAPTER)

class QueryFormAdapter:
    def get_fields(self):
        raise NotImplementedError

    def get_query_language(self, data):
        raise NotImplementedError

    def get_query(self, data):
        raise NotImplementedError


class ConeSearchQueryFormAdapter(ConeSearchBaseClass, QueryFormAdapter):

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

    def get_query(self, data, user):

        resources = self.get_resources()
        schema_name = resources[data['table']]['schema_name']
        table_name = resources[data['table']]['table_name']
        column_names = resources[data['table']]['column_names']

        try:
            columns = self.get_columns(user, schema_name, table_name, column_names)
        except NotFound as e:
            raise ValidationError({"query": {"messages": [str(e)]}}) from e

        columns = [row["name"] if isinstance(row, dict) else row for row in columns]

        return self.sql_pattern.format(schema=schema_name,
                                        table=table_name,
                                        columns=', '.join(columns),
                                        RA=data['ra'], DEC=data['dec'], SR=data['radius']).strip()