import os
import inspect

from kombu import Exchange, Queue

from django.utils.translation import ugettext_lazy as _

# second entry in the call stach is the script that imported settings.py
# this is the BASE_DIR/PROJECT_DIR/settings/__init__.py file
settings_init_filename = inspect.stack()[1][1]

PROJECT_DIR = os.path.dirname(os.path.dirname(settings_init_filename))
BASE_DIR = os.path.dirname(PROJECT_DIR)
DAIQUIRI_APP = os.path.basename(PROJECT_DIR)

DEBUG = False

SITE_ID = 1

HTTPS = False

SECRET_KEY = 'this is not a very secret key'

ALLOWED_HOSTS = ['localhost']

INTERNAL_IPS = ('127.0.0.1',)

ROOT_URLCONF = DAIQUIRI_APP + '.urls'

WSGI_APPLICATION = DAIQUIRI_APP + '.wsgi.application'

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
    'djangobower',
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
    os.path.join(BASE_DIR, 'static/'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
    'djangobower.finders.BowerFinder',
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

BOWER_COMPONENTS_ROOT = os.path.join(BASE_DIR, 'bower_root/')

BOWER_INSTALLED_APPS = (
    'angular#1.5.8',
    'angular-resource#1.5.8',
    'bootstrap#3.3.7',
    'ngInfiniteScroll#1.3.0',
    'codemirror#~5.18.2',
    'components-font-awesome#~4.6.3',
    'moment#~2.14.1',
    'angular-file-saver'
)

SETTINGS_EXPORT = [
    'LOGIN_URL',
    'LOGOUT_URL',
    'QUERY'
]

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_FROM = 'info@example.com'

TAP_ACCESS_LEVEL = 'PUBLIC'

SENDFILE_BACKEND = 'sendfile.backends.simple'

CELERY_BROKER_URL = 'amqp://'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_TASK_DEFAULT_QUEUE = 'daiquiri'
CELERY_TASK_ACKS_LATE = True
CELERY_TASK_QUEUES = (
    Queue('daiquiri', Exchange('daiquiri'), routing_key='daiquiri'),
    Queue('download', Exchange('download'), routing_key='download'),
    Queue('query', Exchange('query'), routing_key='query', queue_arguments={'x-max-priority': 5}),
)
