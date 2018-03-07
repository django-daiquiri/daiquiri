import os

from daiquiri.core.settings.base import BASE_DIR

DAIQUIRI_APPS = [
    'daiquiri.archive',
    'daiquiri.auth',
    'daiquiri.contact',
    'daiquiri.core',
    'daiquiri.files',
    'daiquiri.jobs',
    'daiquiri.meetings',
    'daiquiri.metadata',
    'daiquiri.query',
    'daiquiri.serve',
    'daiquiri.stats',
    'daiquiri.tap',
    'daiquiri.uws'
]

INSTALLED_APPS = []

FIXTURE_DIRS = (
    os.path.join(BASE_DIR, 'fixtures'),
)

REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.ScopedRateThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'query.create': '1000/second'
    }
}

AUTH_SIGNUP = True
AUTH_WORKFLOW = 'confirmation'

ARCHIVE_ANONYMOUS = False
ARCHIVE_BASE_PATH = os.path.join(BASE_DIR, 'files')

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

SERVE_DOWNLOAD_DIR = os.path.join(BASE_DIR, 'files')
