SECRET_KEY = 'this is a not very secret key'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'daiquiri_app',
        'USER': 'root'
    },
    'tap': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'TAP_SCHEMA',
        'USER': 'root'
    },
    'data': {
        'ENGINE': 'django.db.backends.mysql',
        'USER': 'root'
    }
}

LOGGING_DIR = '/tmp'
QUERY_DOWNLOAD_DIR = '/tmp'
