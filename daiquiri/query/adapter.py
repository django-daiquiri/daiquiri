from django.conf import settings
from django.utils.module_loading import import_string

conesearch_adapter_class = import_string(settings.CONESEARCH_ADAPTER)

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
        return conesearch_adapter_class.get_query_language(data)

    def get_query(self, data):
        schema_name = data['table'].split('.')[0]
        table_name = data['table'].split('.')[1]
        columns = self.get_columns(table_name)
        return conesearch_adapter_class.sql_pattern.format(schema=schema_name,
                        table = table_name,
                        columns = columns,
                        RA=data['ra'], DEC=data['dec'], SR=data['radius']).strip()
