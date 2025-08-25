import os
from pathlib import Path
from . import ADDITIONAL_APPS, BASE_DIR, DJANGO_APPS
import sys

SITE_URL = 'http://testserver'
SITE_CREATED = '2020-01-01'

PASSWORD_HASHERS = ('django.contrib.auth.hashers.MD5PasswordHasher',)

FIXTURE_DIRS = [Path(BASE_DIR) / 'testing' / 'fixtures']

INSTALLED_APPS = [
    *DJANGO_APPS,
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
    'daiquiri.uws',
    *ADDITIONAL_APPS,
]

REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': ('rest_framework.throttling.ScopedRateThrottle',),
    'DEFAULT_THROTTLE_RATES': {'query.create': '1000/second'},
}

ARCHIVE_DOWNLOAD_DIR = os.path.join(BASE_DIR, 'download')

AUTH_SIGNUP = True
AUTH_WORKFLOW = 'confirmation'

FILES_BASE_PATH = os.path.join(BASE_DIR, 'files')

MEETINGS_PARTICIPANT_DETAIL_KEYS = [
    {'key': 'affiliation', 'label': 'Affiliation', 'data_type': 'text', 'required': True},
    {
        'key': 'dinner',
        'label': 'Conference dinner',
        'data_type': 'radio',
        'required': True,
        'options': [{'id': 'yes', 'label': 'yes'}, {'id': 'no', 'label': 'no'}],
    },
]

QUERY_DOWNLOAD_DIR = os.path.join(BASE_DIR, 'download')
QUERY_UPLOAD_DIR = os.path.join(BASE_DIR, 'upload')

SERVE_DOWNLOAD_DIR = os.path.join(BASE_DIR, 'files')

SECRET_KEY = 'this is a not very secret key'

# all test databases need to have different name or they will not be picked up by django
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'daiquiri_app',
        'USER': 'daiquiri_app',
        'PASSWORD': 'daiquiri_app',
        'HOST': '127.0.0.1',
        'TEST': {
            'NAME': 'test_daiquiri_app',
        },
    },
    'data': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'daiquiri_dataaaaaaaaaaaaaa',
        'USER': 'daiquiri_data',
        'PASSWORD': 'daiquiri_data',
        'HOST': '127.0.0.1',
        'TEST': {
            'NAME': 'test_daiquiri_data',
        },
    },
    'tap': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'daiquiri_data',
        'USER': 'daiquiri_data',
        'PASSWORD': 'daiquiri_data',
        'HOST': '127.0.0.1',
        'TEST': {
            'NAME': 'test_daiquiri_tap',
        },
    },
    'oai': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'daiquiri_data',
        'USER': 'daiquiri_data',
        'PASSWORD': 'daiquiri_data',
        'HOST': '127.0.0.1',
        'TEST': {
            'NAME': 'test_daiquiri_oai',
        },
    },
}

ADAPTER_DATABASE = 'daiquiri.core.adapter.database.postgres.PostgreSQLAdapter'
ADAPTER_DOWNLOAD = 'daiquiri.core.adapter.download.pgdump.PgDumpAdapter'

TAP_SCHEMA = 'public'
OAI_SCHEMA = 'public'
