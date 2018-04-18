import os

from .base import BASE_DIR

ASYNC = False

IPV4_PRIVACY_MASK = 16
IPV6_PRIVACY_MASK = 32

DOWNLOAD_PREPEND = {}

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
ARCHIVE_BASE_PATH = os.path.join(BASE_DIR, 'files')
ARCHIVE_DOWNLOAD_DIR = os.path.join(BASE_DIR, 'download')

AUTH_SIGNUP = False
AUTH_WORKFLOW = None
AUTH_DETAIL_KEYS = []

CONESEARCH_ADAPTER = 'daiquiri.conesearch.adapter.SimpleConeSearchAdapter'
CONESEARCH_ANONYMOUS = False

CUTOUT_ADAPTER = 'daiquiri.cutout.adapter.SimpleCutOutAdapter'
CUTOUT_ANONYMOUS = False

FILES_BASE_PATH = os.path.join(BASE_DIR, 'files')
FILES_SEARCH_URL = None

MEETINGS_CONTRIBUTION_TYPES = [
    (None, 'no contribution'),
    ('talk', 'Talk'),
    ('poster', 'Poster')
]
MEETINGS_PARTICIPANT_DETAIL_KEYS = []
MEETINGS_ABSTRACT_MAX_LENGTH = 2000

METADATA_COLUMN_PERMISSIONS = False

QUERY_ANONYMOUS = False
QUERY_USER_SCHEMA_PREFIX = 'daiquiri_user_'
QUERY_QUOTA = {
    'anonymous': '100Mb',
    'user': '100Mb',
    'users': {},
    'groups': {}
}
QUERY_MAX_ACTIVE_JOBS = {
    'anonymous': '1'
}
QUERY_QUEUES = [
    {
        'key': 'default',
        'label': 'Default',
        'timeout': 10,
        'priority': 1
    }
]
QUERY_LANGUAGES = [
    {
        'key': 'adql',
        'version': 2.0,
        'label': 'ADQL',
        'description': '',
        'quote_char': '"'
    }
]
QUERY_FORMS = [
    {
        'key': 'sql',
        'label': 'SQL query',
        'service': 'query/js/forms/sql.js',
        'template': 'query/query_form_sql.html'
    }
]
QUERY_DROPDOWNS = [
    {
        'key': 'simbad',
        'service': 'query/js/dropdowns/simbad.js',
        'template': 'query/query_dropdown_simbad.html',
        'options': {
            'url': 'http://simbad.u-strasbg.fr/simbad/sim-id'
        }
    },
    {
        'key': 'vizier',
        'service': 'query/js/dropdowns/vizier.js',
        'template': 'query/query_dropdown_vizier.html',
        'options': {
            'url': 'http://vizier.u-strasbg.fr/viz-bin/votable',
            'catalogs': ['I/322A', 'I/259']
        }
    }
]
QUERY_DOWNLOAD_DIR = os.path.join(BASE_DIR, 'download')
QUERY_DEFAULT_DOWNLOAD_FORMAT = 'votable'
QUERY_DOWNLOAD_FORMATS = [
    {
        'key': 'csv',
        'extension': 'csv',
        'content_type': 'text/csv',
        'label': 'Comma separated Values',
        'help': 'A text file with a line for each row of the table. The fields are delimited by a comma and quoted by double quotes. Use this option for a later import into a spreadsheed application or a custom script. Use this option if you are unsure what to use.'
    },
    {
        'key': 'votable',
        'extension': 'xml',
        'content_type': 'application/xml',
        'label': 'IVOA VOTable XML file - TABLEDATA serialization',
        'help': 'A XML file using the IVOA VOTable format. Use this option if you intend to use VO compatible software to further process the data.'
    }
]

SERVE_DOWNLOAD_DIR = os.path.join(BASE_DIR, 'download')
SERVE_RESOLVER = None

STATS_RESOURCE_TYPES = [
    {
        'key': 'ARCHIVE_DOWNLOAD',
        'label': 'Archive downloads'
    },
    {
        'key': 'CONESEARCH',
        'label': 'Performed cone searches'
    },
    {
        'key': 'CUTOUT',
        'label': 'Performed cutouts'
    },
    {
        'key': 'FILE',
        'label': 'File downloads'
    },
    {
        'key': 'QUERY_JOB',
        'label': 'Query jobs'
    }
]

UWS_RESOURCES = []

TAP_SCHEMA = 'TAP_SCHEMA'

WORDPRESS_URL = '/cms/'
WORDPRESS_CLI = '/opt/wp-cli/wp'
WORDPRESS_PATH = '/opt/wordpress'
