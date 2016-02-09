SECRET_KEY = 'this is a not very secret key'

SITE_URL = 'http://localhost:8000'

SITE_ID = 1

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'daiquiri',
        'USER': 'postgres'
    }
}
