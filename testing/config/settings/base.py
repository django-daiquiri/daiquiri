import os

from daiquiri.core.settings.base import BASE_DIR

DAIQUIRI_APPS = [
    'daiquiri.archive',
    'daiquiri.auth',
    'daiquiri.contact',
    'daiquiri.core',
    'daiquiri.files',
    'daiquiri.jobs',
    'daiquiri.meetings',
    'daiquiri.metadata',
    'daiquiri.query',
    'daiquiri.serve',
    'daiquiri.stats',
    'daiquiri.tap',
    'daiquiri.uws'
]

INSTALLED_APPS = []

FIXTURE_DIRS = (
    os.path.join(BASE_DIR, 'fixtures'),
)

AUTH_SIGNUP = True

AUTH_WORKFLOW = 'confirmation'

ARCHIVE_ANONYMOUS = False

ARCHIVE_BASE_PATH = os.path.join(BASE_DIR, 'files')
