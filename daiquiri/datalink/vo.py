from django.conf import settings
from django.urls import reverse

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
