DATALINK_CONTENT_TYPE = 'application/x-votable+xml;content=datalink'
DATALINK_FIELDS = [
    {
        'name': 'ID',
        'description': 'Input identifier.',
        'ucd': 'meta.id;meta.ref.url;meta.main'
    },
    {
        'name': 'access_url',
        'description': 'Link to data or service.',
        'ucd': 'meta.ref.url;meta.main'
    },
    {
        'name': 'service_def',
        'description': 'Reference to a service descriptor resource.',
        'ucd': 'meta.ref'
    },
    {
        'name': 'error_message',
        'description': 'Error if an access_url cannot be created.',
        'ucd': 'meta.code.error'
    },
    {
        'name': 'description',
        'description': 'Human-readable text describing this link.',
        'ucd': 'meta.note;meta.main'
    },
    {
        'name': 'semantics',
        'description': 'Term from a controlled vocabulary describing the link.',
        'ucd': 'meta.code;meta.main'
    },
    {
        'name': 'content_type',
        'description': 'Mime-type of the content the link returns.',
        'ucd': 'meta.code.mime'
    },
    {
        'name': 'content_length',
        'description': 'Size of the download the link returns.',
        'ucd': 'phys.size;meta.file'
    }
]
