import os

# include settimgs from daiquiri
from daiquiri.core.settings.base import *
from daiquiri.core.settings.daiquiri import *
from daiquiri.core.settings.logging import *

# include settings from base.py
from .base import *

# include settings from local.py
from .local import *

# include 3rd party apps after the daiquiri apps from base.py
INSTALLED_APPS = DJANGO_APPS + DAIQUIRI_APPS + ADDITIONAL_APPS + INSTALLED_APPS

# prepend the local.BASE_URL to the different URL settings
try:
    LOGIN_URL = BASE_URL + LOGIN_URL
    LOGIN_REDIRECT_URL = BASE_URL + LOGIN_REDIRECT_URL
    LOGOUT_URL = BASE_URL + LOGOUT_URL
    ACCOUNT_LOGOUT_REDIRECT_URL = BASE_URL
    MEDIA_URL = BASE_URL + MEDIA_URL
    STATIC_URL = BASE_URL + STATIC_URL

    CSRF_COOKIE_PATH = BASE_URL + '/'
    LANGUAGE_COOKIE_PATH = BASE_URL + '/'
    SESSION_COOKIE_PATH = BASE_URL + '/'
except NameError:
    pass

# prepend the LOGGING_DIR to the filenames in LOGGING
for handler in LOGGING['handlers'].values():
    if 'filename' in handler:
        handler['filename'] = os.path.join(LOGGING_DIR, handler['filename'])

