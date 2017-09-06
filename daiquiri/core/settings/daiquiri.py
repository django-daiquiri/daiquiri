import os

from .base import BASE_DIR

ASYNC = False

IPV4_PRIVACY_MASK = 16
IPV6_PRIVACY_MASK = 32

AUTH_WORKFLOW = None

AUTH_DETAIL_KEYS = []

QUERY_ANONYMOUS = False

QUERY_USER_DATABASE_PREFIX = 'daiquiri_user_'

QUERY_QUOTA = {
    'anonymous': '100Mb',
    'user': '100Mb',
    'users': {},
    'groups': {}
}

QUERY_QUEUES = [
    {
        'key': 'default',
        'label': 'Default',
        'timeout': 300,
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
    },
    {
        'key': 'box',
        'label': 'Box search',
        'service': 'query/js/forms/box.js',
        'template': 'query/query_form_box.html'
    },
    {
        'key': 'cone',
        'label': 'Cone search',
        'service': 'query/js/forms/cone.js',
        'template': 'query/query_form_cone.html'
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
        'extension': 'votable.xml',
        'content_type': 'application/xml',
        'label': 'IVOA VOTable XML file - TABLEDATA serialization',
        'help': 'A XML file using the IVOA VOTable format. Use this option if you intend to use VO compatible software to further process the data.'
    },
    {
        'key': 'votable-binary',
        'extension': 'votable.binary.xml',
        'content_type': 'application/xml',
        'label': 'IVOA VOTable XML file - BINARY serialization',
        'help': 'A XML file using the IVOA VOTable format (BINARY Serialization). Use this option if you intend to use VO compatible software to process the data and prefer the use of a binary file.'
    },
    {
        'key': 'votable-binary2',
        'extension': 'votable.binary2.xml',
        'content_type': 'application/xml',
        'label': 'IVOA VOTable XML file - BINARY 2 serialization',
        'help': 'A XML file using the IVOA VOTable format (BINARY2 Serialization). Use this option if you intend to use VO compatible software to process the data and prefer the use of a binary file.'
    }
]

SERVE_DOWNLOAD_DIR = os.path.join(BASE_DIR, 'download')

TAP_ACCESS_LEVEL = 'PUBLIC'

UWS_RESOURCES = []

WORDPRESS_URL = '/cms/'
WORDPRESS_CLI = '/opt/wp-cli/wp'
WORDPRESS_PATH = '/opt/wordpress'
