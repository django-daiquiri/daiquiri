import os

from daiquiri.core.settings.base import BASE_DIR

DAIQUIRI_APPS = [
    'daiquiri.auth',
    'daiquiri.contact',
    'daiquiri.core',
    'daiquiri.jobs',
    'daiquiri.meetings',
    'daiquiri.metadata',
    'daiquiri.query',
    'daiquiri.serve',
    'daiquiri.tap',
    'daiquiri.uws'
]

INSTALLED_APPS = []

FIXTURE_DIRS = (
    os.path.join(BASE_DIR, 'fixtures'),
)

AUTH_WORKFLOW = 'confirmation'
