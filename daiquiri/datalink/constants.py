DATALINK_CONTENT_TYPE = 'application/x-votable+xml;content=datalink'
DATALINK_TABLE = {
    'name': 'datalink',
    'description': 'The table of datalinks for the service',
    'order': 4,
    'access_level': 'PUBLIC',
    'metadata_access_level': 'PUBLIC'
}
DATALINK_FIELDS = [
    {
        'name': 'ID',
        'order': 1,
        'description': 'Input identifier.',
        'ucd': 'meta.id;meta.main',
        'datatype': 'char',
        'arraysize': None,
        'std': True,
        'access_level': 'PUBLIC',
        'metadata_access_level': 'PUBLIC'
    },
    {
        'name': 'access_url',
        'order': 2,
        'description': 'Link to data or service.',
        'ucd': 'meta.ref.url',
        'datatype': 'char',
        'arraysize': None,
        'std': True,
        'access_level': 'PUBLIC',
        'metadata_access_level': 'PUBLIC'
    },
    {
        'name': 'service_def',
        'order': 3,
        'description': 'Reference to a service descriptor resource.',
        'ucd': 'meta.ref',
        'datatype': 'char',
        'arraysize': None,
        'std': True,
        'access_level': 'PUBLIC',
        'metadata_access_level': 'PUBLIC'
    },
    {
        'name': 'error_message',
        'order': 4,
        'description': 'Error if an access_url cannot be created.',
        'ucd': 'meta.code.error',
        'datatype': 'char',
        'arraysize': None,
        'std': True,
        'access_level': 'PUBLIC',
        'metadata_access_level': 'PUBLIC'
    },
    {
        'name': 'description',
        'order': 5,
        'description': 'Human-readable text describing this link.',
        'ucd': 'meta.note',
        'datatype': 'char',
        'arraysize': None,
        'std': True,
        'access_level': 'PUBLIC',
        'metadata_access_level': 'PUBLIC'
    },
    {
        'name': 'semantics',
        'order': 6,
        'description': 'Term from a controlled vocabulary describing the link.',
        'ucd': 'meta.code',
        'datatype': 'char',
        'arraysize': None,
        'std': True,
        'access_level': 'PUBLIC',
        'metadata_access_level': 'PUBLIC'
    },
    {
        'name': 'content_type',
        'order': 7,
        'description': 'Mime-type of the content the link returns.',
        'ucd': 'meta.code.mime',
        'datatype': 'char',
        'arraysize': None,
        'std': True,
        'access_level': 'PUBLIC',
        'metadata_access_level': 'PUBLIC'
    },
    {
        'name': 'content_length',
        'order': 8,
        'description': 'Size of the download the link returns.',
        'ucd': 'phys.size;meta.file',
        'datatype': 'long',
        'arraysize': None,
        'unit': 'byte',
        'std': True,
        'access_level': 'PUBLIC',
        'metadata_access_level': 'PUBLIC'
    }
]

DATALINK_RELATION_TYPES = {
    'IsCitedBy': '{} is cited by the linked resource.',
    'Cites': '{} cites the linked resource.',
    'IsSupplementTo': '{} is supplement to the linked resource.',
    'IsSupplementedBy': '{} is supplemented by the linked resource.',
    'IsContinuedBy': '{} is continued by the linked resource.',
    'Continues': '{} continues the linked resource.',
    'IsDescribedBy': '{} is described by the linked resource.',
    'Describes': '{} describes the linked resource.',
    'HasMetadata': 'the linked resource is metadata for {}.',
    'IsMetadataFor': '{} is metadata for the linked resource.',
    'HasVersion': 'the linked resource is a version of {}.',
    'IsVersionOf': '{} is a version of the linked resource.',
    'IsNewVersionOf': '{} is a newer version of the linked resource.',
    'IsPreviousVersionOf': '{} is a previous version of the linked resource.',
    'IsPartOf': '{} is part of the linked resource.',
    'HasPart': 'the linked resource is a part of {}.',
    'IsPublishedIn': '{} is published in the linked resource.',
    'IsReferencedBy': '{} is referenced by the linked resource.',
    'References': '{} references the linked resource.',
    'IsDocumentedBy': '{} is documented by the linked resource.',
    'Documents': '{} documents the linked resource.',
    'IsCompiledBy': '{} is compiled by the linked resource.',
    'Compiles': '{} compiles the linked resource.',
    'IsVariantFormOf': '{} is a variant form of the linked resource.',
    'IsOriginalFormOf': '{} is the original form of the linked resource.',
    'IsIdenticalTo': '{} is identical to the linked resource.',
    'IsReviewedBy': '{} is reviewed by the linked resource.',
    'Reviews': '{} reviews the linked resource.',
    'IsDerivedFrom': '{} is derived from the linked resource.',
    'IsSourceOf': '{} is the source of the linked resource.',
    'IsRequiredBy': '{} is required by the linked resource.',
    'Requires': '{} requires the linked resource.',
    'IsObsoletedBy': '{} is obsoleted by the linked resource.',
    'Obsoletes': '{} obsoletes the linked resource.'
}
