import daiquiri.core.env as env

CONESEARCH_ADAPTER = 'daiquiri.conesearch.adapter.BaseConeSearchAdapter'
CONESEARCH_ANONYMOUS = False

#CONESEARCH_SCHEMA = env.get('CONESEARCH_SCHEMA')
#CONESEARCH_TABLE = env.get('CONESEARCH_TABLE')

CONESEARCH_SUBJECTS = [
    'cone search'
]

CONESEARCH_RESOURCES = {}

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
        'RA': 20,
        'DEC': 20,
        'SR': 10,
    }
MAX_RECORDS = 10000
