import os
from . import BASE_DIR, DJANGO_APPS, ADDITIONAL_APPS

SITE_URL = 'http://testserver'

INSTALLED_APPS = DJANGO_APPS + [
    'daiquiri.archive',
    'daiquiri.auth',
    'daiquiri.conesearch',
    'daiquiri.contact',
    'daiquiri.core',
    'daiquiri.files',
    'daiquiri.jobs',
    'daiquiri.meetings',
    'daiquiri.metadata',
    'daiquiri.oai',
    'daiquiri.query',
    'daiquiri.registry',
    'daiquiri.serve',
    'daiquiri.stats',
    'daiquiri.tap',
    'daiquiri.uws'
] + ADDITIONAL_APPS

REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.ScopedRateThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'query.create': '1000/second'
    }
}

ARCHIVE_DOWNLOAD_DIR = os.path.join(BASE_DIR, 'download')

AUTH_SIGNUP = True
AUTH_WORKFLOW = 'confirmation'

ARCHIVE_ANONYMOUS = False
ARCHIVE_BASE_PATH = os.path.join(BASE_DIR, 'files')

FILES_BASE_PATH = os.path.join(BASE_DIR, 'files')

MEETINGS_PARTICIPANT_DETAIL_KEYS = [
    {
        'key': 'affiliation',
        'label': 'Affiliation',
        'data_type': 'text',
        'required': True
    },
    {
        'key': 'dinner',
        'label': 'Conference dinner',
        'data_type': 'radio',
        'required': True,
        'options': [
            {'id': 'yes', 'label': 'yes'},
            {'id': 'no', 'label': 'no'}
        ]
    }
]

QUERY_DOWNLOAD_DIR = os.path.join(BASE_DIR, 'download')
QUERY_UPLOAD_DIR = os.path.join(BASE_DIR, 'upload')

SERVE_DOWNLOAD_DIR = os.path.join(BASE_DIR, 'files')
