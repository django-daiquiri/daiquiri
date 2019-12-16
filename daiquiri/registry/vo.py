from django.conf import settings
from django.urls import reverse


def get_curation():
    return {
        'publisher': settings.SITE_PUBLISHER,
        'date': settings.SITE_UPDATED,
        'creator': {
            'name': settings.SITE_CREATOR
        },
        'contact': settings.SITE_CONTACT
    }


def get_resource():
    return {
        'service': 'registry',
        'identifier': 'ivo://%s/registry' % settings.SITE_IDENTIFIER,
        'title': '%s Registry' % settings.SITE_TITLE,
        'curation': get_curation(),
        'content': {
            'type': 'Registry',
            'description': 'The publishing registry for %s.' % settings.SITE_IDENTIFIER,
            'referenceURL': settings.SITE_URL.rstrip('/') + reverse('registry:root')
        },
        'capabilities': get_capabilities(),
        'managed_authority': settings.SITE_IDENTIFIER,
        'type': 'vg:Registry',
        'created': settings.SITE_CREATED,
        'updated': settings.SITE_UPDATED,
        'vodataservice_type': 'vg:Registry',
        'voresource_status': 'active'
    }


def get_authority_resource():
    return {
        'service': 'authority',
        'identifier': 'ivo://%s' % settings.SITE_IDENTIFIER,
        'title': settings.SITE_IDENTIFIER,
        'curation': get_curation(),
        'content': {
            'type': 'Authority',
            'description': 'The authority for %s.' % settings.SITE_IDENTIFIER,
            'referenceURL': settings.SITE_URL.rstrip('/')
        },
        'capabilities': [],
        'managing_org': settings.SITE_PUBLISHER,
        'type': 'vg:Authority',
        'created': settings.SITE_CREATED,
        'updated': settings.SITE_UPDATED,
    }


def get_web_resource():
    return {
        'service': 'web',
        'identifier': 'ivo://%s/web' % settings.SITE_IDENTIFIER,
        'title': settings.SITE_IDENTIFIER,
        'curation': get_curation(),
        'content': {
            'type': 'Catalog',
            'description': 'The main web service for %s.' % settings.SITE_IDENTIFIER,
            'referenceURL': settings.SITE_URL.rstrip('/')
        },
        'capabilities': [
            {
                'interface': {
                    'type': 'vr:WebBrowser',
                    'access_url': {
                        'use': 'full',
                        'url': settings.SITE_URL.rstrip('/')
                    }
                }
            }
        ],
        'type': 'vg:CatalogResource',
        'created': settings.SITE_CREATED,
        'updated': settings.SITE_UPDATED,
    }


def get_availability():
    return {
        'available': 'true',
        'note': 'service is accepting queries'
    }


def get_capabilities():
    return [
        {
            'id': 'ivo://ivoa.net/std/Registry',
            'type': 'vg:Harvest',
            'interface': {
                'type': 'vg:OAIHTTP',
                'role': 'std',
                'access_url': {
                    'use': 'base',
                    'url': settings.SITE_URL.rstrip('/') + reverse('oai:root')
                }
            },
            'max_records': settings.OAI_PAGE_SIZE
        },
        {
            'id': 'ivo://ivoa.net/std/VOSI#availability"',
            'interface': {
                'type': 'vs:ParamHTTP',
                'role': 'std',
                'access_url': {
                    'use': 'full',
                    'url': settings.SITE_URL.rstrip('/') + reverse('registry:availability')
                }
            }
        },
        {
            'id': 'ivo://ivoa.net/std/VOSI#capabilities',
            'interface': {
                'type': 'vs:ParamHTTP',
                'role': 'std',
                'access_url': {
                    'use': 'full',
                    'url': settings.SITE_URL.rstrip('/') + reverse('registry:capabilities')
                }
            }
        }
    ]
