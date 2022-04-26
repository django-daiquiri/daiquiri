import daiquiri.core.env as env

ASYNC = env.get_bool('ASYNC')

QUEUES = [
    {
        'key': 'default',
        'concurency': 1
    },
    {
        'key': 'download',
        'concurency': 1
    }
]

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
SITE_CREATED = None
SITE_UPDATED = None
SITE_LANGUAGE = 'en'
SITE_SUBJECTS = [
    {
        'subject': 'Astronomy',
        'schemeURI': 'http://id.loc.gov/authorities/subjects',
        'valueURI': 'http://id.loc.gov/authorities/subjects/sh85009003'
    }
]
SITE_TYPE = 'service'
SITE_LOGO_URL = None
