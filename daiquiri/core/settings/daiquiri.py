import daiquiri.core.env as env

ASYNC = env.get_bool('ASYNC')

QUEUES = [{'key': 'default', 'concurrency': 1}, {'key': 'download', 'concurrency': 1}]

IPV4_PRIVACY_MASK = 16
IPV6_PRIVACY_MASK = 32

SITE_URL = env.get('SITE_URL')

SITE_IDENTIFIER = None
SITE_TITLE = None
SITE_DESCRIPTION = None
SITE_LICENSE = None
SITE_CREATOR = None
SITE_CONTACT = None
SITE_PUBLISHER = None
SITE_PUBLISHER_PROPERTIES = {}
# SITE_PUBLISHER_PROPERTIES = {
#     'publisherIdentifier': 'https://ror.org/<id>',
#     'publisherIdentifierScheme': 'ROR',
#     'schemeURI': 'https:/ror.org/',
# }

SITE_CREATED = None
SITE_UPDATED = None
SITE_LANGUAGE = 'en'
SITE_SUBJECTS = [
    {
        'subject': 'Astronomy',
        'subjectScheme': 'Library of Congress Subject Headings (LCSH)',
        'schemeURI': 'http://id.loc.gov/authorities/subjects',
        'valueURI': 'http://id.loc.gov/authorities/subjects/sh85009003',
    }
]
SITE_TYPE = 'service'
SITE_LOGO_URL = None
