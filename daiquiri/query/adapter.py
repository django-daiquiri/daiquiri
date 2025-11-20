from django.conf import settings

from rest_framework.exceptions import ValidationError

from daiquiri.conesearch.adapter import  BaseConeSearchAdapter


class QueryFormAdapter:
    def get_fields(self):
        raise NotImplementedError

    def get_query_language(self, data):
        raise NotImplementedError

    def get_query(self, data):
        raise NotImplementedError


class ConeSearchQueryFormAdapter(QueryFormAdapter):

    def get_resources(self):
        return settings.CONESEARCH_RESOURCES.values()

    def get_tables(self):
        return [{'id':t, 'value': t, 'label': t} for
                t in dict.fromkeys(f"{v['schema_name']}.{v['table_name']}" for v in self.get_resources())]

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

    def get_columns(self, table):
        columns = next(
        (v['column_names'] for v in self.get_resources()
         if v['table_name'] == table),[])
        return ', '.join(columns)

    def get_query_language(self, data):
        return 'ADQL' #'postgresql-16.2'

    def validate_input(self, data):
        ranges = settings.CONESEARCH_RANGES
        errors = {"query": {"messages": [] }}

        if not ranges['RA']['min'] <= data['ra'] <= ranges['RA']['max']:
            errors['query']['messages'].append(f"RA must be between {ranges['RA']['min']} and {ranges['RA']['max']}")

        if not ranges['DEC']['min'] <= data['dec'] <= ranges['DEC']['max']:
            errors['query']['messages'].append(f"DEC must be between {ranges['DEC']['min']} and {ranges['DEC']['max']}")


        if not ranges['SR']['min'] <= data['radius'] <= ranges['SR']['max']:
            errors['query']['messages'].append(f"Radius must be between {ranges['SR']['min']} and {ranges['SR']['max']}")

        if errors['query']['messages']:
            raise ValidationError(errors)

    def get_query(self, data):
        self.validate_input(data)
        schema_name = data['table'].split('.')[0]
        table_name = data['table'].split('.')[1]
        columns = self.get_columns(table_name)
        return BaseConeSearchAdapter.sql_pattern.format(schema=schema_name,
                        table = table_name,
                        columns = columns,
                        RA=data['ra'], DEC=data['dec'], SR=data['radius']).strip()
