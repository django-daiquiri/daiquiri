CONESEARCH_ADAPTER = 'daiquiri.conesearch.adapter.BaseConeSearchAdapter'
CONESEARCH_ANONYMOUS = False

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
    'RA': 0.0,
    'DEC': 0.0,
    'SR': 1.0,
}

CONESEARCH_MAX_RECORDS = 10000
