from . import TAP_SCHEMA, OAI_SCHEMA

SECRET_KEY = 'this is a not very secret key'

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
        'OPTIONS': {
            'options': '-c search_path=public'
        },
        'NAME': 'daiquiri_data',
        'USER': 'daiquiri_data',
        'PASSWORD': 'daiquiri_data',
        'HOST': '127.0.0.1',
        'TEST': {
            'NAME': 'test_daiquiri_data',
        },
    },
    'tap': {
        'ENGINE': 'django.db.backends.postgresql',
        'OPTIONS': {
            'options': '-c search_path=%s' % TAP_SCHEMA
        },
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
        'OPTIONS': {
            'options': '-c search_path=%s' % OAI_SCHEMA
        },
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
