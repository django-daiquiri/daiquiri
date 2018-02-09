SECRET_KEY = 'this is a not very secret key'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'daiquiri_app',
        'USER': 'root'
    },
    'tap': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'TAP_SCHEMA',
        'USER': 'root'
    },
    'data': {
        'ENGINE': 'django.db.backends.postgresql',
        'USER': 'root'
    }
}

LOGGING_DIR = '/tmp'
QUERY_DOWNLOAD_DIR = '/tmp'
