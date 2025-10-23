from importlib.util import find_spec
from pathlib import Path

from django.utils.translation import gettext_lazy as _

import daiquiri.core.env as env

try:
    CONFIG_DIR = Path(find_spec('config').origin).parent
    BASE_DIR = CONFIG_DIR.parent
    DAIQUIRI_APP = BASE_DIR.name.replace('-', '_')
except AttributeError:
    BASE_DIR = Path().cwd()
    DAIQUIRI_APP = None

BASE_URL = env.get_url('BASE_URL', '/')

DEBUG = env.get_bool('DEBUG')

SECRET_KEY = env.get('SECRET_KEY')

ALLOWED_HOSTS = env.get_list('ALLOWED_HOSTS', ['localhost', '127.0.0.1', '::1'])

if env.get_bool('PROXY'):
    USE_X_FORWARDED_HOST = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

INTERNAL_IPS = env.get_list('INTERNAL_IPS', ['127.0.0.1'])

ADMINS = env.get_email_list('ADMINS')

SITE_ID = 1

ROOT_URLCONF = 'config.urls'

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': env.get_database('app'),
    'data': env.get_database('data'),
    'tap': env.get_database('data'),
    'oai': env.get_database('data'),
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

if DATABASES['tap'].get('ENGINE') == 'django.db.backends.postgresql':
    DATABASES['tap']['OPTIONS'] = {
        'options': '-c search_path={}'.format(env.get('TAP_SCHEMA', 'tap_schema'))
    }
elif DATABASES['tap'].get('ENGINE') == 'django.db.backends.mysql':
    DATABASES['tap']['NAME'] = env.get('TAP_SCHEMA', 'tap_schema')

if DATABASES['oai'].get('ENGINE') == 'django.db.backends.postgresql':
    DATABASES['oai']['OPTIONS'] = {
        'options': '-c search_path={}'.format(env.get('OAI_SCHEMA', 'oai_schema'))
    }
elif DATABASES['oai'].get('ENGINE') == 'django.db.backends.mysql':
    DATABASES['oai']['NAME'] = env.get('OAI_SCHEMA', 'oai_schema')

ADAPTER_DATABASE = env.get_database_adapter()
ADAPTER_DOWNLOAD = env.get_download_adapter()

if DATABASES['data'].get('ENGINE') == 'django.db.backends.postgresql':
    USER_TABLESPACE = env.get('USER_TABLESPACE', 'pg_default')
else:
    USER_TABLESPACE = None

DATABASE_ROUTERS = [
    'daiquiri.core.routers.TapRouter',
    'daiquiri.core.routers.OaiRouter',
    'daiquiri.core.routers.DataRouter',
]

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.forms',
]

ADDITIONAL_APPS = [
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'django_extensions',
    'markdown',
    'widget_tweaks',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'rules',
    'django_sendfile',
    'honeypot',
]

DJANGO_MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.sites.middleware.CurrentSiteMiddleware',
]

ADDITIONAL_MIDDLEWARE = [
    'allauth.account.middleware.AccountMiddleware',
]

MIDDLEWARE = [
    'daiquiri.core.middleware.MultipleProxyMiddleware',
    *DJANGO_MIDDLEWARE,
    *ADDITIONAL_MIDDLEWARE,
]

TEMPLATES_DIR = BASE_DIR / 'templates/'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIR] if TEMPLATES_DIR.exists() else [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django_settings_export.settings_export',
            ],
        },
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = env.get('TIME_ZONE', 'UTC')

LOCALE_PATHS = (BASE_DIR / 'locale/',)

LANGUAGES = (('en', _('English')),)

USE_I18N = True

USE_TZ = True

LOGIN_URL = BASE_URL + 'accounts/login/'
LOGIN_REDIRECT_URL = BASE_URL
LOGOUT_URL = BASE_URL + 'accounts/logout/'
LOGOUT_REDIRECT_URL = BASE_URL

CSRF_COOKIE_PATH = BASE_URL
LANGUAGE_COOKIE_PATH = BASE_URL
SESSION_COOKIE_PATH = BASE_URL

MEDIA_URL = BASE_URL + 'media/'
MEDIA_ROOT = BASE_DIR / 'media_root/'

STATIC_URL = BASE_URL + 'static/'
STATIC_ROOT = BASE_DIR / 'static_root/'

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

FIXTURE_DIRS = (BASE_DIR / 'fixtures',)

FORM_RENDERER = 'daiquiri.core.forms.DaiquiriFormRenderer'

AUTHENTICATION_BACKENDS = (
    'rules.permissions.ObjectPermissionBackend',
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_LOGOUT_REDIRECT_URL = BASE_URL
ACCOUNT_ADAPTER = 'daiquiri.auth.adapter.DaiquiriAccountAdapter'
ACCOUNT_SIGNUP_FORM_CLASS = 'daiquiri.auth.forms.SignupForm'
ACCOUNT_USER_DISPLAY = 'daiquiri.auth.utils.get_full_name'
ACCOUNT_USERNAME_VALIDATORS = 'daiquiri.auth.validators.username_validators'
ACCOUNT_USERNAME_MIN_LENGTH = 4
ACCOUNT_PASSWORD_MIN_LENGTH = 8
ACCOUNT_EMAIL_MAX_LENGTH = 190
ACCOUNT_SIGNUP_FIELDS = ['email*', 'username*', 'password1*', 'password2*']
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 7
# 'mandatory' or 'optional'
ACCOUNT_EMAIL_VERIFICATION = env.get('ACCOUNT_EMAIL_VERIFICATION', 'mandatory')
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True

SOCIALACCOUNT_ADAPTER = 'daiquiri.auth.adapter.DaiquiriSocialAccountAdapter'
SOCIALACCOUNT_AUTO_SIGNUP = False

REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': ('rest_framework.throttling.ScopedRateThrottle',),
    'DEFAULT_THROTTLE_RATES': {'query.create': '10/second'},
}

SETTINGS_EXPORT = [
    'ACCOUNT_LOGOUT_ON_GET',
    'AUTH_WORKFLOW',
    'AUTH_TERMS_OF_USE',
    'LOGIN_URL',
    'LOGOUT_URL',
    'METADATA_COLUMN_PERMISSIONS',
    'SITE_PUBLISHER',
    'SITE_URL',
    'SITE_TITLE',
    'STATS_RESOURCE_TYPES',
]

DEFAULT_FROM_EMAIL = env.get('DEFAULT_FROM_EMAIL', 'info@example.com')
EMAIL_BACKEND = env.get('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_REPLY_TO = env.get('EMAIL_REPLY_TO')
EMAIL_HOST = env.get('EMAIL_HOST')
EMAIL_HOST_USER = env.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env.get('EMAIL_HOST_PASSWORD')
EMAIL_PORT = env.get('EMAIL_PORT', '25')
EMAIL_USE_TLS = env.get_bool('EMAIL_USE_TLS')

SENDFILE_BACKEND = env.get('SENDFILE_BACKEND', 'django_sendfile.backends.simple')
SENDFILE_ROOT = env.get('SENDFILE_ROOT')
SENDFILE_URL = env.get('SENDFILE_URL')

MEMCACHE_KEY_PREFIX = env.get('MEMCACHE_KEY_PREFIX')
if MEMCACHE_KEY_PREFIX:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
            'LOCATION': '127.0.0.1:11211',
            'KEY_PREFIX': MEMCACHE_KEY_PREFIX,
        }
    }

CELERY_BROKER_URL = env.get('CELERY_BROKER_URL', 'amqp://')
CELERY_BIN = env.get('CELERY_BIN', 'celery')
CELERY_PIDFILE_PATH = env.get_abspath('CELERY_PIDFILE_PATH')
CELERY_LOG_LEVEL = env.get('CELERY_LOG_LEVEL', 'INFO')
CELERY_LOG_PATH = env.get_abspath('CELERY_LOG_PATH')

HONEYPOT_ENABLED = True
HONEYPOT_FIELD_NAME = 'Phone'
HONEYPOT_FIELD_VALUE = ''
HONEYPOT_FIELD_HIDDEN = True

PASSWORD_HASHERS = [
    'daiquiri.core.hashers.CrypdSHA512PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
]
