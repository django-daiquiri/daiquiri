SECRET_KEY = 'this is a not very secret key'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgrseql',
        'NAME': 'daiquiri_app',
        'USER': 'daiquiri_app',
        'PASSWORD': 'daiquiri_app'
    },
    'tap': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'TAP_SCHEMA',
        'USER': 'daiquiri_tap',
        'PASSWORD': 'daiquiri_tap'
    },
    'data': {
        'ENGINE': 'django.db.backends.postgresql',
        'USER': 'daiquiri_data',
        'PASSWORD': 'daiquiri_data'
    }
}
