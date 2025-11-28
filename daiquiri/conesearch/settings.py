CONESEARCH_ADAPTER = 'daiquiri.conesearch.adapter.BaseConeSearchAdapter'
CONESEARCH_ANONYMOUS = False

CONESEARCH_SUBJECTS = [
    'cone search'
]

CONESEARCH_RESOURCES = {}
# EXAMPLE:
# CONESEARCH_RESOURCES = {
#       '[schema_name].[table_name]': {
#           'schema_name': '[schema_name]',
#           'table_name': '[table_name]',
#           'column_names': ['source_id', 'ra', 'dec'],
#           'coordinates_columns': {'RA': 'ra', 'DEC': 'dec' },
#       },
#       '[schema_name].[table_name]': {
#           'schema_name': '[schema_name]',
#           'table_name': '[table_name]',
#           'column_names': ['source_id', 'ra_component', 'dec_component'],
#           'coordinates_columns': {'RA': 'ra_component', 'DEC': 'dec_component' },
#       },
# }

CONESEARCH_RANGES = {
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

CONESEARCH_DEFAULTS = {
    'RA': 0.0,
    'DEC': 0.0,
    'SR': 1.0,
}

CONESEARCH_MAX_RECORDS = 10000
