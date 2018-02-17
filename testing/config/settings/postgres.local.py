SECRET_KEY = 'this is a not very secret key'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'daiquiri_app',
    },
    'tap': {
        'ENGINE': 'django.db.backends.postgresql',
        'OPTIONS': {
            'options': '-c search_path=TAP_SCHEMA'
        },
        'NAME': 'daiquiri_data',
    },
    'data': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'daiquiri_data',
    }
}

ADAPTER_DATABASE = 'daiquiri.core.adapter.database.postgres.PostgreSQLAdapter'
ADAPTER_DOWNLOAD = 'daiquiri.core.adapter.download.pgdump.PgDumpAdapter'
