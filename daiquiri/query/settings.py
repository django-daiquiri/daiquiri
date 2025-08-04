import daiquiri.core.env as env

QUERY_DOWNLOAD_DIR = env.get_abspath('QUERY_DOWNLOAD_DIR')
QUERY_UPLOAD_DIR = env.get_abspath('QUERY_UPLOAD_DIR')

QUERY_ANONYMOUS = False
QUERY_USER_SCHEMA_PREFIX = 'daiquiri_user_'

QUERY_QUOTA = {
    'anonymous': '100Mb',
    'user': '10000Mb',
    'users': {},
    'groups': {}
}

QUERY_SYNC_TIMEOUT = 5

QUERY_MAX_ACTIVE_JOBS = {'anonymous': '1'}

QUERY_QUEUES = [
    {
        'key': 'short',
        'label': '30 seconds',
        'timeout': 30,
        'access_level': 'PUBLIC',
        'groups': [],
    },
    {
        'key': 'long',
        'label': '1 Hour',
        'timeout': 3600,
        'access_level': 'PUBLIC',
        'groups': [],
    },
]
QUERY_LANGUAGES = [
    {
        'key': 'adql',
        'version': 2.0,
        'label': 'ADQL',
        'description': '',
        'quote_char': '"',
    }
]
QUERY_FORMS = [
    {
        'key': 'sql',
        'label': 'SQL query',
        'template': 'query/query_form_sql.html',
    },
    {
        'key': 'upload',
        'label': 'Upload VOTable',
        'template': 'query/query_form_upload.html',
    },
]
QUERY_PLOTS = [
    {
        'key': 'scatter_plot',
        'label': 'Scatter',
        'is_active': True,
    },
    {
        'key': 'scatter_cmap_plot',
        'label': 'Scatter (color coded)',
        'is_active': True,
    },
    {
        'key': 'histogram',
        'label': 'Histogram',
        'is_active': True,
    },
]

QUERY_DROPDOWNS = [
    {
        'key': 'schemas',
        'label': 'Database',
    },
    {
        'key': 'columns',
        'label': 'Columns',
    },
    {
        'key': 'functions',
        'label': 'Functions',
    },
    {
        'key': 'simbad',
        'label': 'Simbad',
        'options': {'url': 'http://simbad.u-strasbg.fr/simbad/sim-id'},
    },
    {
        'key': 'vizier',
        'label': 'VizieR',
        'options': {
            'url': 'http://vizier.u-strasbg.fr/viz-bin/votable',
            'catalogs': ['I/322A', 'I/259'],
        },
    },
    {
        'key': 'examples',
        'label': 'Examples',
        'classes': 'ms-auto',
    },
]
QUERY_DOWNLOADS = [
    {
        'key': 'table',
        'model': 'daiquiri.query.models.DownloadJob',
        'params': ['format_key'],
    },
    {
        'key': 'archive',
        'model': 'daiquiri.query.models.QueryArchiveJob',
        'params': ['column_name'],
    },
]
QUERY_DEFAULT_DOWNLOAD_FORMAT = 'votable'
QUERY_DOWNLOAD_FORMATS = [
    {
        'key': 'votable',
        'extension': 'xml',
        'content_type': 'application/xml',
        'label': 'IVOA VOTable',
        'help': 'A XML file using the IVOA VOTable format. Use this option if you intend '
        'to use VO compatible software to further process the data.',
    },
    {
        'key': 'csv',
        'extension': 'csv',
        'content_type': 'text/csv',
        'label': 'Comma-separated Values',
        'help': 'A text file with a line for each row of the table. The fields are delimited '
        'by a comma and quoted by double quotes.',
    },
    {
        'key': 'fits',
        'extension': 'fits',
        'content_type': 'application/fits',
        'label': 'FITS',
        'help': 'Flexible Image Transport System (FITS) file format.',
    },
    {
        'key': 'parquet',
        'extension': 'parquet',
        'content_type': 'application/parquet',
        'label': 'Parquet',
        'help': 'Apache Parquet file format.',
    },
]
QUERY_UPLOAD = True
QUERY_UPLOAD_LIMIT = {
    'anonymous': '10Mb',
    'user': '100Mb', 'users': {},
    'groups': {}
}
QUERY_PROCESSOR_CACHE = True
