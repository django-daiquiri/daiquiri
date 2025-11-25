# ruff: noqa: F403, F405, I001, RUF005
'''
Generic settings to be used with daiquiri-admin outside of an daiquiri-app.
'''
from pathlib import Path

from daiquiri.core.settings.django import *
from daiquiri.core.settings.daiquiri import *
from daiquiri.core.settings.logging import *

from daiquiri.auth.settings import *
from daiquiri.conesearch.settings import *
from daiquiri.contact.settings import *
from daiquiri.cutout.settings import *
from daiquiri.datalink.settings import *
from daiquiri.files.settings import *
from daiquiri.metadata.settings import *
from daiquiri.oai.settings import *
from daiquiri.query.settings import *
from daiquiri.registry.settings import *
from daiquiri.serve.settings import *
from daiquiri.stats.settings import *
from daiquiri.tap.settings import *

INSTALLED_APPS = DJANGO_APPS + [
    'daiquiri.auth',
    'daiquiri.conesearch',
    'daiquiri.contact',
    'daiquiri.core',
    'daiquiri.datalink',
    'daiquiri.files',
    'daiquiri.jobs',
    'daiquiri.metadata',
    'daiquiri.oai',
    'daiquiri.query',
    'daiquiri.registry',
    'daiquiri.serve',
    'daiquiri.stats',
    'daiquiri.tap',
    'daiquiri.uws',
]

MIDDLEWARE = [
    'daiquiri.core.middleware.MultipleProxyMiddleware',
    *DJANGO_MIDDLEWARE,
]

ROOT_URLCONF = ''

DATABASES = {}

STATIC_ROOT = 'static_root'

FILES_BASE_PATH = QUERY_DOWNLOAD_DIR = Path().cwd()
