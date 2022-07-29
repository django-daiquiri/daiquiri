import os

from . import ADDITIONAL_APPS, BASE_DIR, DJANGO_APPS

SITE_URL = 'http://testserver'
SITE_CREATED = '2020-01-01'

INSTALLED_APPS = DJANGO_APPS + [
    'daiquiri.auth',
    'daiquiri.conesearch',
    'daiquiri.contact',
    'daiquiri.core',
    'daiquiri.datalink',
    'daiquiri.files',
    'daiquiri.jobs',
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
