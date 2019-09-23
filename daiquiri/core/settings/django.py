import imp
import os

from django.utils.translation import ugettext_lazy as _

import daiquiri.core.env as env

CONFIG_DIR = imp.find_module('config')[1]
BASE_DIR = os.path.dirname(CONFIG_DIR)
DAIQUIRI_APP = os.path.basename(BASE_DIR).replace('-', '_')

BASE_URL = env.get_url('BASE_URL', '/')

DEBUG = env.get_bool('DEBUG')

SECRET_KEY = env.get('SECRET_KEY')

ALLOWED_HOSTS = env.get_list('ALLOWED_HOSTS', ['localhost', '127.0.0.1', '::1'])

INTERNAL_IPS = env.get_list('INTERNAL_IPS', ['127.0.0.1'])

SITE_ID = 1

ROOT_URLCONF = 'config.urls'

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    'default': env.get_database('app'),
    'data': env.get_database('data'),
    'tap': env.get_database('data'),
    'oai': env.get_database('data'),
}

if DATABASES['tap'].get('ENGINE') == 'django.db.backends.postgresql':
    DATABASES['tap']['OPTIONS'] = {
        'options': '-c search_path=%s' % env.get('TAP_SCHEMA', 'tap_schema')
    }
elif DATABASES['tap'].get('ENGINE') == 'django.db.backends.mysql':
    DATABASES['tap']['NAME'] = env.get('TAP_SCHEMA', 'tap_schema')

if DATABASES['oai'].get('ENGINE') == 'django.db.backends.postgresql':
    DATABASES['oai']['OPTIONS'] = {
        'options': '-c search_path=%s' % env.get('OAI_SCHEMA', 'oai_schema')
    }
elif DATABASES['oai'].get('ENGINE') == 'django.db.backends.mysql':
    DATABASES['oai']['NAME'] = env.get('OAI_SCHEMA', 'oai_schema')

ADAPTER_DATABASE = env.get_database_adapter()
ADAPTER_DOWNLOAD = env.get_download_adapter()

DATABASE_ROUTERS = [
    'daiquiri.oai.routers.OaiRouter',
    'daiquiri.tap.routers.TapRouter',
    'daiquiri.core.routers.DataRouter'
]

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
]

ADDITIONAL_APPS = [
    'rest_framework',
    'rest_framework.authtoken',
    'django_filters',
    'django_extensions',
    'vendor_files',
    'markdown',
    'compressor',
    'widget_tweaks',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'rules'
]

MIDDLEWARE = [
    'daiquiri.core.middleware.MultipleProxyMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.contrib.sites.middleware.CurrentSiteMiddleware'
]

TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates/')
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIR] if os.path.exists(TEMPLATES_DIR) else [],
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

COMPRESS_PRECOMPILERS = (
    ('text/x-scss', 'django_libsass.SassCompiler'),
)

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale/'),
)

LANGUAGES = (
    ('en', _('English')),
)

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOGIN_URL = BASE_URL + 'accounts/login/'
LOGIN_REDIRECT_URL = BASE_URL
LOGOUT_URL = BASE_URL + 'accounts/logout/'
LOGOUT_REDIRECT_URL = BASE_URL

CSRF_COOKIE_PATH = BASE_URL
LANGUAGE_COOKIE_PATH = BASE_URL
SESSION_COOKIE_PATH = BASE_URL

MEDIA_URL = BASE_URL + 'media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media_root/')

STATIC_URL = BASE_URL + 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static_root/')

STATICFILES_DIR = os.path.join(BASE_DIR, 'static/')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'vendor/')]
STATICFILES_DIRS += [STATICFILES_DIR] if os.path.exists(STATICFILES_DIR) else []

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder'
)

FIXTURE_DIRS = (
    os.path.join(BASE_DIR, 'fixtures'),
)

AUTHENTICATION_BACKENDS = (
    'rules.permissions.ObjectPermissionBackend',
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

ACCOUNT_LOGOUT_ON_GET = False
ACCOUNT_LOGOUT_REDIRECT_URL = BASE_URL
ACCOUNT_ADAPTER = 'daiquiri.auth.adapter.DaiquiriAccountAdapter'
ACCOUNT_SIGNUP_FORM_CLASS = 'daiquiri.auth.forms.SignupForm'
ACCOUNT_USER_DISPLAY = 'daiquiri.auth.utils.get_full_name'
ACCOUNT_USERNAME_MIN_LENGTH = 4
ACCOUNT_PASSWORD_MIN_LENGTH = 4
ACCOUNT_EMAIL_MAX_LENGTH = 190
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 7
# 'mandatory' or 'optional'
ACCOUNT_EMAIL_VERIFICATION = env.get('ACCOUNT_EMAIL_VERIFICATION', 'mandatory')
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True

SOCIALACCOUNT_ADAPTER = 'daiquiri.auth.adapter.DaiquiriSocialAccountAdapter'

REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.ScopedRateThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'query.create': '10/second'
    }
}

SETTINGS_EXPORT = [
    'LOGIN_URL',
    'LOGOUT_URL',
    'ARCHIVE_COLUMNS',
    'ACCOUNT_LOGOUT_ON_GET',
    'AUTH_WORKFLOW',
    'AUTH_TERMS_OF_USE',
    'METADATA_COLUMN_PERMISSIONS',
    'QUERY_DROPDOWNS',
    'QUERY_FORMS',
    'QUERY_DOWNLOAD_FORMATS',
    'QUERY_UPLOAD',
    'STATS_RESOURCE_TYPES'
]

DEFAULT_FROM_EMAIL = env.get('DEFAULT_FROM_EMAIL', 'info@example.com')
EMAIL_BACKEND = env.get('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_REPLY_TO = env.get('EMAIL_REPLY_TO')
EMAIL_HOST = env.get('EMAIL_HOST')
EMAIL_HOST_USER = env.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env.get('EMAIL_HOST_PASSWORD')
EMAIL_PORT = env.get('EMAIL_PORT', '25')
EMAIL_USE_TLS = env.get_bool('EMAIL_USE_TLS')

SENDFILE_BACKEND = env.get('SENDFILE_BACKEND', 'sendfile.backends.simple')
