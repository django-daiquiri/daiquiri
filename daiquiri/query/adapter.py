from django.conf import settings


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
                t in dict.fromkeys(v['table_name'] for v in self.get_resources())]

    def get_fields(self):
        return [
            {
                'key': 'table',
                'type': 'subselect',
                'label': 'Select a Table',
                'placeholder': 'Select a table',
                'help': 'Choose a Table',
                'width': 12,
                'options': self.get_tables(),
            },
            {
                'key': 'ra',
                'type': 'number',
                'label': 'RA',
                'help': 'Right ascension in degrees (decimal form)',
                'default_value': 200.0,
                'width': 4,
            },
            {
                'key': 'dec',
                'type': 'number',
                'label': 'DEC',
                'help': 'Declination in degrees (decimal form)',
                'default_value': 45.0,
                'width': 4,
            },
            {
                'key': 'radius',
                'type': 'number',
                'label': 'Radius',
                'help': 'Radius in degrees',
                'default_value': 0.05,
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

    def get_query(self, data):
        columns = self.get_columns(data['table'])
        return """
        select {columns}, distance(point(ra, dec), point({ra}, {dec})) as angdist 
        from gaiadr3.{table}
        where 1=contains(point(ra, dec), circle(point({ra}, {dec}), {radius}))
        """.format(columns=columns, **data).strip()