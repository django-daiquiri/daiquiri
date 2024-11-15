from django.conf import settings
from django.urls import reverse

from daiquiri.core.vo import get_curation

from .constants import DATALINK_CONTENT_TYPE


def get_availability():
    return {
        'available': 'true',
        'note': 'service is accepting queries'
    }


def get_capabilities():
    return [
        {
            'id': 'ivo://ivoa.net/std/DataLink#links-1.0',
            'interface': {
                'type': 'vs:ParamHTTP',
                'role': 'std',
                'version': '1.0',
                'access_url': {
                    'use': 'base',
                    'url': settings.SITE_URL.rstrip('/') + reverse('datalink:link-list').rstrip('/')
                },
                'query_types': ['GET', 'POST'],
                'result_type': DATALINK_CONTENT_TYPE,
                'params': [
                    {
                        'name': 'ID',
                        'std': 'true',
                        'use': 'required',
                        'description': 'publisher dataset identifier',
                        'ucd': 'meta.id;meta.main',
                        'datatype': 'string'
                    }
                ]
            }
        }
    ]


def get_resource():
    return {
        'service': 'datalink',
        'identifier': f'ivo://{settings.SITE_IDENTIFIER}/datalink',
        'title': f'{settings.SITE_TITLE} Datalink Service',
        'curation': get_curation(),
        'content': {
            'subjects': [],
            'type': '',
            'description': f'The Datalink Service for {settings.SITE_IDENTIFIER}.',
            'referenceURL': settings.SITE_URL.rstrip('/') + reverse('datalink:root').rstrip('/')
        },
        'capabilities': get_capabilities(),
        'created': settings.SITE_CREATED,
        'updated': settings.SITE_UPDATED,
        'type': '',
        'status': 'active'
    }


def get_service():
    return {
        'params': [
            {
                'name': 'standardID',
                'datatype': 'char',
                'arraysize': '*',
                'value': 'ivo://ivoa.net/std/DataLink#links-1.0'
            },
                                {
                'name': 'accessURL',
                'datatype': 'char',
                'arraysize': '*',
                'value': settings.SITE_URL.rstrip('/') + '/datalink/links'
            }
        ],
        'groups': [
            {
                'name': 'inputParams',
                'params': [
                    {
                        'name': 'ID',
                        'datatype': 'char',
                        'arraysize': '*',
                        'value': '',
                        'ref': 'datalinkID'
                    }
                ]
            }
        ]
    }
