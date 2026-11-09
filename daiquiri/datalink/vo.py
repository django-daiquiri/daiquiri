from django.conf import settings
from django.urls import reverse

from daiquiri.core.vo import get_curation

from .constants import DATALINK_CONTENT_TYPE


def get_availability():
    return {
        'available': 'true',
        'note': 'service is accepting queries'
    }


def get_capabilities(path='/'):
    link_list = get_link_list_name(path)
    return [
        {
            'id': 'ivo://ivoa.net/std/DataLink#links-1.0',
            'interface': {
                'type': 'vs:ParamHTTP',
                'role': 'std',
                'version': '1.0',
                'access_url': {
                    'use': 'base',
                    'url': settings.SITE_URL.rstrip('/') + reverse(f'datalink:{link_list}')
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


def get_service(path=None, field_id='datalinkID'):
    if path is None:
        access_url = settings.SITE_URL.rstrip('/') + '/datalink/links'
    else:
        access_url = settings.SITE_URL.rstrip('/') + reverse(f'datalink:{get_link_list_name(path)}')
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
                'value': access_url
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
                        'ref': field_id
                    }
                ]
            }
        ]
    }


def get_link_list_name(path):
    return 'link-list' if path == '/' else f'{path.strip("/").replace("/", "-")}-link-list'


def get_service_descriptors(fields):
    services = []
    for field in fields:
        ucd = field.get('ucd') or ''
        path = '/' if 'meta.id' in ucd and 'meta.ref' in ucd else field.get('datalink_path')
        if path:
            field_id = 'datalinkID' if not services else f'datalinkID{len(services) + 1}'
            field['datalink_id'] = field_id
            services.append(get_service(path, field_id))
    return services
