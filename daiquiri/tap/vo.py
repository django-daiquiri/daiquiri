from django.conf import settings
from django.urls import reverse

from daiquiri.core.constants import ACCESS_LEVEL_PUBLIC
from daiquiri.core.vo import get_curation
from daiquiri.jobs.utils import get_max_records
from daiquiri.metadata.models import Schema
from daiquiri.query.utils import get_quota

from .serializers import SchemaSerializer


def get_resource():
    return {
        'service': 'tap',
        'identifier': f'ivo://{settings.SITE_IDENTIFIER}/tap',
        'title': f'{settings.SITE_TITLE} TAP Service',
        'curation': get_curation(),
        'content': {
            'subjects': settings.TAP_SUBJECTS,
            'type': 'Catalog',
            'description': f'The TAP Service registry for {settings.SITE_IDENTIFIER}.',
            'referenceURL': settings.SITE_URL.rstrip('/') + reverse('tap:root').rstrip('/')
        },
        'capabilities': get_capabilities(),
        'tableset': get_tableset(),
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
            'id': 'ivo://ivoa.net/std/TAP',
            'type': 'tr:TableAccess',
            'interface': {
                'type': 'vs:ParamHTTP',
                'role': 'std',
                'access_url': {
                    'use': 'base',
                    'url': settings.SITE_URL.rstrip('/') + reverse('tap:root').rstrip('/')
                }
            },
            'languages': [{
                'name': language['key'],
                'version': language['version'],
                'description': language['description'],
            } for language in settings.QUERY_LANGUAGES],
            'output_formats': [{
                'mime': format['content_type'],
                'alias': format['key'],
            } for format in settings.QUERY_DOWNLOAD_FORMATS],
            'upload_methods': [
                'ivo://ivoa.net/std/TAPRegExt#upload-inline',
                'ivo://ivoa.net/std/TAPRegExt#upload-https',
            ] if settings.TAP_UPLOAD else [],
            'upload_limit': int(get_quota(None, quota_settings='QUERY_UPLOAD_LIMIT')),
            'output_limit': int(get_max_records(None))
        },
        {
            'id': 'ivo://ivoa.net/std/TAP#async-1.1',
            'interface': {
                'type': 'vs:ParamHTTP',
                'role': 'std',
                'version': '1.1',
                'access_url': {
                    'use': 'base',
                    'url': settings.SITE_URL.rstrip('/') + reverse('tap:async-list').rstrip('/')
                }
            }
        },
        {
            'id': 'ivo://ivoa.net/std/TAP#sync-1.1',
            'interface': {
                'type': 'vs:ParamHTTP',
                'role': 'std',
                'version': '1.1',
                'access_url': {
                    'use': 'base',
                    'url': settings.SITE_URL.rstrip('/') + reverse('tap:sync-list').rstrip('/')
                }
            }
        },
        {
            'id': 'ivo://ivoa.net/std/VOSI#capabilities',
            'interface': {
                'type': 'vs:ParamHTTP',
                'access_url': {
                    'use': 'full',
                    'url': settings.SITE_URL.rstrip('/') + reverse('tap:capabilities').rstrip('/')
                }
            }
        },
        {
            'id': 'ivo://ivoa.net/std/VOSI#tables',
            'interface': {
                'type': 'vs:ParamHTTP',
                'access_url': {
                    'use': 'full',
                    'url': settings.SITE_URL.rstrip('/') + reverse('tap:tables').rstrip('/')
                }
            }
        },
        {
            'id': 'ivo://ivoa.net/std/DALI#examples',
            'interface': {
                'type': 'vr:WebBrowser',
                'access_url': {
                    'use': 'full',
                    'url': settings.SITE_URL.rstrip('/') + reverse('tap:examples').rstrip('/')
                }
            }
        }
    ]


def get_tableset():
    queryset = Schema.objects.filter(metadata_access_level=ACCESS_LEVEL_PUBLIC, published__isnull=False)
    serializer = SchemaSerializer(queryset, many=True)
    return serializer.data
