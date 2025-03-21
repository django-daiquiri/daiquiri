from django.conf import settings
from django.urls import reverse

from daiquiri.core.vo import get_curation

from .adapter import ConeSearchAdapter


def get_resource():
    return {
        'service': 'conesearch',
        'identifier': f'ivo://{settings.SITE_IDENTIFIER}/conesearch',
        'title': f'{settings.SITE_TITLE} Cone Search Service',
        'curation': get_curation(),
        'content': {
            'subjects': settings.CONESEARCH_SUBJECTS,
            'type': 'Catalog',
            'description': f'The Cone Search Service for {settings.SITE_IDENTIFIER}.',
            'referenceURL': settings.SITE_URL.rstrip('/')  # + reverse('conesearch:root')
        },
        'capabilities': get_capabilities(),
        'created': settings.SITE_CREATED,
        'updated': settings.SITE_UPDATED,
        'type': 'vs:CatalogService',
        'status': 'active'
    }


def get_availability():
    return {
        'available': 'true',
        'note': 'service is accepting queries'
    }


def get_capabilities():
    adapter = ConeSearchAdapter()

    return [
        {
            'id': 'ivo://ivoa.net/std/ConeSearch',
            'type': 'cs:ConeSearch',
            'interface': {
                'type': 'vs:ParamHTTP',
                'role': 'std',
                'access_url': {
                    'use': 'base',
                    'url': settings.SITE_URL.rstrip('/') + reverse('conesearch:search', args=[resource])
                },
                'query_types': ['GET'],
                'result_type': 'application/x-votable+xml',
                'params': [
                    {
                        'std': 'true',
                        'name': 'RA',
                        'description': 'Right Ascension (ICRS decimal)',
                        'ucd': 'pos.eq.ra',
                        'datatype': 'real'
                    },
                    {
                        'std': 'true',
                        'name': 'DEC',
                        'description': 'Declination (ICRS decimal)',
                        'ucd': 'pos.eq.dec',
                        'datatype': 'real'
                    },
                    {
                        'std': 'true',
                        'name': 'SR',
                        'description': 'Search radius',
                        'datatype': 'real'
                    },
                    {
                        'std': 'true',
                        'name': 'VERB',
                        'description': 'Exhaustiveness of column selection. VERB=1 only returns the most important ' \
                                       'columns, VERB=2 selects the columns deemed useful to the average user, ' \
                                       'VERB=3 returns a table with all available columns.',
                        'datatype': 'integer'
                    }
                ]
            },
            'max_sr': adapter.ranges['SR']['max'],
            'max_records': adapter.max_records,
            'verbosity': 'true',
            'test_query': {
                'ra': adapter.defaults.get('RA'),
                'dec': adapter.defaults.get('DEC'),
                'sr': adapter.defaults.get('SR')
            }
        } for resource in adapter.get_resources()
    ]
