import imp
import os

from django.utils.translation import ugettext_lazy as _

CONFIG_DIR = imp.find_module('config')[1]
BASE_DIR = os.path.dirname(CONFIG_DIR)
DAIQUIRI_APP = os.path.basename(BASE_DIR).replace('-', '_')

DEBUG = False

SITE_ID = 1

HTTPS = False

SECRET_KEY = 'this is not a very secret key'

ALLOWED_HOSTS = ['localhost']

INTERNAL_IPS = ('127.0.0.1',)

ROOT_URLCONF = 'config.urls'

WSGI_APPLICATION = 'config.wsgi.application'

DATABASE_ROUTERS = ['daiquiri.tap.routers.TapRouter', 'daiquiri.core.routers.DataRouter']

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
    'markdown',
    'compressor',
    'widget_tweaks',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'rules'
]

MIDDLEWARE_CLASSES = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sites.middleware.CurrentSiteMiddleware'
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates/')],
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

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_URL = '/accounts/logout/'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media_root/')

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static_root/')

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'vendor/'),
    os.path.join(BASE_DIR, 'static/'),
)

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

ACCOUNT_ADAPTER = 'daiquiri.auth.adapter.DaiquiriAccountAdapter'
ACCOUNT_SIGNUP_FORM_CLASS = 'daiquiri.auth.forms.SignupForm'
ACCOUNT_USER_DISPLAY = 'daiquiri.auth.utils.get_full_name'
ACCOUNT_EMAIL_MAX_LENGTH = 190
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 7
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True

SOCIALACCOUNT_ADAPTER = 'daiquiri.auth.adapter.DaiquiriSocialAccountAdapter'

SETTINGS_EXPORT = [
    'LOGIN_URL',
    'LOGOUT_URL',
    'AUTH_WORKFLOW',
    'QUERY_DROPDOWNS',
    'QUERY_FORMS',
    'QUERY_DOWNLOAD_FORMATS'
]

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_FROM = 'info@example.com'

SENDFILE_BACKEND = 'sendfile.backends.simple'

LOGGING_DIR = os.path.join(BASE_DIR, 'log')
