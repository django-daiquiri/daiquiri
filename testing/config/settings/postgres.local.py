SECRET_KEY = 'this is a not very secret key'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'daiquiri_app',
        'USER': 'postgres',
    },
    'tap': {
        'ENGINE': 'django.db.backends.postgresql',
        'OPTIONS': {
            'options': '-c search_path=TAP_SCHEMA'
        },
        'NAME': 'daiquiri_data',
        'USER': 'postgres'
    },
    'data': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'daiquiri_data',
        'USER': 'postgres'
    }
}

ADAPTER_DATABASE = 'daiquiri.core.adapter.database.postgres.PostgreSQLAdapter'
ADAPTER_DOWNLOAD = 'daiquiri.core.adapter.download.pgdump.PgDumpAdapter'
