import os

from django.utils.translation import ugettext_lazy as _

from .base import BASE_DIR

ASYNC = False

IPV4_PRIVACY_MASK = 16
IPV6_PRIVACY_MASK = 32

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
AUTH_TERMS_OF_USE = False

CONESEARCH_ADAPTER = 'daiquiri.conesearch.adapter.SimpleConeSearchAdapter'
CONESEARCH_ANONYMOUS = False

CUTOUT_ADAPTER = 'daiquiri.cutout.adapter.SimpleCutOutAdapter'
CUTOUT_ANONYMOUS = False

FILES_BASE_PATH = os.path.join(BASE_DIR, 'files')
FILES_BASE_URL = None

MEETINGS_CONTRIBUTION_TYPES = [
    ('talk', _('Talk')),
    ('poster', _('Poster'))
]
MEETINGS_PAYMENT_CHOICES = (
    ('cash', _('cash')),
    ('wire', _('wire transfer')),
)

MEETINGS_PARTICIPANT_DETAIL_KEYS = []
MEETINGS_ABSTRACT_MAX_LENGTH = 2000

METADATA_COLUMN_PERMISSIONS = False
METADATA_BASE_URL = None
METADATA_PUBLISHER = None
METADATA_LANGUAGE = 'en'

QUERY_ANONYMOUS = False
QUERY_USER_SCHEMA_PREFIX = 'daiquiri_user_'
QUERY_QUOTA = {
    'anonymous': '100Mb',
    'user': '10000Mb',
    'users': {},
    'groups': {}
}
QUERY_SYNC_TIMEOUT = 5
QUERY_MAX_ACTIVE_JOBS = {
    'anonymous': '1'
}
QUERY_QUEUES = [
    {
        'key': 'default',
        'label': 'Default',
        'timeout': 10,
        'priority': 1,
        'access_level': 'PUBLIC',
        'groups': []
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
    },
    {
        'key': 'upload',
        'label': 'Upload VOTable',
        'service': 'query/js/forms/upload.js',
        'template': 'query/query_form_upload.html'
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
        'key': 'votable',
        'extension': 'xml',
        'content_type': 'application/xml',
        'label': 'IVOA VOTable XML file - TABLEDATA serialization',
        'help': 'A XML file using the IVOA VOTable format. Use this option if you intend to use VO compatible software to further process the data.'
    },
    {
        'key': 'csv',
        'extension': 'csv',
        'content_type': 'text/csv',
        'label': 'Comma separated Values',
        'help': 'A text file with a line for each row of the table. The fields are delimited by a comma and quoted by double quotes. Use this option for a later import into a spreadsheed application or a custom script. Use this option if you are unsure what to use.'
    },
    {
        'key': 'fits',
        'extension': 'fits',
        'content_type': 'application/fits',
        'label': 'FITS',
        'help': 'Flexible Image Transport System (FITS) file format.'
    }
]
QUERY_UPLOAD = True
QUERY_UPLOAD_LIMIT = {
    'anonymous': '10Mb',
    'user': '100Mb',
    'users': {},
    'groups': {}
}

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
        'key': 'QUERY',
        'label': 'Queries'
    }
]

UWS_RESOURCES = []

TAP_SCHEMA = 'TAP_SCHEMA'
TAP_UPLOAD = 'TAP_UPLOAD'

WORDPRESS_URL = '/cms/'
WORDPRESS_CLI = '/opt/wp-cli/wp'
WORDPRESS_PATH = None
WORDPRESS_SSH = None
