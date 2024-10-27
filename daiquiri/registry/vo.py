from django.apps import apps
from django.conf import settings
from django.urls import reverse

from daiquiri.core.vo import get_curation


def get_resource():
    return {
        'service': 'registry',
        'identifier': f'ivo://{settings.SITE_IDENTIFIER}/registry',
        'title': f'{settings.SITE_TITLE} Registry',
        'curation': get_curation(),
        'content': {
            'subjects': settings.REGISTRY_SUBJECTS,
            'type': 'Registry',
            'description': f'The publishing registry for {settings.SITE_IDENTIFIER}.',
            'referenceURL': settings.SITE_URL.rstrip('/') + reverse('registry:root')
        },
        'capabilities': get_capabilities(),
        'full': 'false',
        'managed_authority': settings.SITE_IDENTIFIER,
        'created': settings.SITE_CREATED,
        'updated': settings.SITE_UPDATED,
        'type': 'vg:Registry',
        'status': 'active',
        'tableset': get_tap_tableset()
    }


def get_authority_resource():
    return {
        'service': 'authority',
        'identifier': f'ivo://{settings.SITE_IDENTIFIER}',
        'title': settings.SITE_IDENTIFIER,
        'curation': get_curation(),
        'content': {
            'subjects': settings.REGISTRY_AUTHORITY_SUBJECTS,
            'type': 'Authority',
            'description': f'The authority for {settings.SITE_IDENTIFIER}.',
            'referenceURL': settings.SITE_URL.rstrip('/')
        },
        'capabilities': [],
        'managing_org': settings.SITE_PUBLISHER,
        'created': settings.SITE_CREATED,
        'updated': settings.SITE_UPDATED,
        'type': 'vg:Authority',
        'status': 'active'
    }


def get_web_resource():
    return {
        'service': 'web',
        'identifier': f'ivo://{settings.SITE_IDENTIFIER}/web',
        'title': settings.SITE_IDENTIFIER,
        'curation': get_curation(),
        'content': {
            'subjects': settings.REGISTRY_WEB_SUBJECTS,
            'type': 'Catalog',
            'description': f'The main web service for {settings.SITE_IDENTIFIER}.',
            'referenceURL': settings.SITE_URL.rstrip('/')
        },
        'capabilities': [
            {
                'interface': {
                    'subjects': ['Web browser'],
                    'type': 'vr:WebBrowser',
                    'access_url': {
                        'use': 'full',
                        'url': settings.SITE_URL.rstrip('/')
                    }
                }
            }
        ],
        'created': settings.SITE_CREATED,
        'updated': settings.SITE_UPDATED,
        'type': 'vs:CatalogResource',
        'status': 'active'
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


def get_tap_tableset():
    if apps.is_installed('daiquiri.tap'):
        from daiquiri.tap.vo import get_tableset
        return get_tableset()
