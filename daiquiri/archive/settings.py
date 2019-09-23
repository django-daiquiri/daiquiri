import daiquiri.core.env as env

ARCHIVE_BASE_PATH = env.get_abspath('ARCHIVE_BASE_PATH')
ARCHIVE_DOWNLOAD_DIR = env.get_abspath('ARCHIVE_DOWNLOAD_DIR')

ARCHIVE_ANONYMOUS = False
ARCHIVE_SCHEMA = 'daiquiri_archive'
ARCHIVE_TABLE = 'files'
ARCHIVE_COLUMNS = [
    {
        'name': 'id',
        'hidden': True
    },
    {
        'name': 'timestamp',
        'label': 'Timestamp'
    },
    {
        'name': 'file',
        'label': 'Filename',
        'ucd': 'meta.file'
    },
    {
        'name': 'collection',
        'hidden': True
    },
    {
        'name': 'path',
        'hidden': True
    }
]
