import daiquiri.core.env as env

CONESEARCH_ADAPTER = 'daiquiri.conesearch.adapter.SimpleConeSearchAdapter'
CONESEARCH_ANONYMOUS = False

CONESEARCH_SCHEMA = env.get('CONESEARCH_SCHEMA')
CONESEARCH_TABLE = env.get('CONESEARCH_TABLE')

CONESEARCH_SUBJECTS = [
    'cone search'
]
