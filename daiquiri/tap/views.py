from django.conf import settings
from django.http import HttpResponse
from django.urls import reverse

from daiquiri.query.models import Example

from .models import Schema
from .serializers import ExampleSerializer, SchemaSerializer
from .renderers import (
    ExampleRenderer,
    AvailabilityRenderer,
    CapabilitiesRenderer,
    TablesetRenderer
)


def examples(request):
    serializer = ExampleSerializer(Example.objects.all(), many=True)
    return HttpResponse(ExampleRenderer().render(serializer.data), content_type="application/xml")


def availability(request):
    data = {
        'available': 'true',
        'note': 'service is accepting queries'
    }
    return HttpResponse(AvailabilityRenderer().render(data), content_type="application/xml")


def capabilities(request):
    data = [
        {
            'schemaID': 'ivo://ivoa.net/std/TAP',
            'interface': {
                'attrs': {
                    'xsi:type': 'vs:ParamHTTP',
                    'role': 'std'
                },
                'accessURL': {
                    'attrs': {},
                    'text': request.build_absolute_uri(reverse('tap_root'))
                }
            },
            'languages': [{
                'name': language['key'],
                'version': language['version'],
                'description': language['description'],
            } for language in settings.QUERY['query_languages']]

        },
        {
            'schemaID': 'ivo://ivoa.net/std/TAP#async-1.1',
            'interface': {
                'attrs': {
                    'xsi:type': 'vs:ParamHTTP',
                    'role': 'std',
                    'version': '1.1'
                },
                'accessURL': {
                    'attrs': {
                        'use': 'base'
                    },
                    'text': request.build_absolute_uri(reverse('tap_async-list'))
                }
            }
        },
        {
            'schemaID': 'ivo://ivoa.net/std/TAP#sync-1.1',
            'interface': {
            'attrs': {
                'xsi:type': 'vs:ParamHTTP',
                'role': 'std',
                'version': '1.1'
                },
                'accessURL': {
                    'attrs': {
                        'use': 'base'
                    },
                    'text': request.build_absolute_uri(reverse('tap_sync-list'))
                }
            }
        },
        {
            'schemaID': 'ivo://ivoa.net/std/VOSI#capabilities',
            'interface': {
            'attrs': {
                'xsi:type': 'vs:ParamHTTP',
                },
                'accessURL': {
                    'attrs': {
                        'use': 'full'
                    },
                    'text': request.build_absolute_uri(reverse('tap_capabilities'))
                }
            }
        },
        {
            'schemaID': 'ivo://ivoa.net/std/VOSI#tables',
            'interface': {
            'attrs': {
                'xsi:type': 'vs:ParamHTTP',
                },
                'accessURL': {
                    'attrs': {
                        'use': 'full'
                    },
                    'text': request.build_absolute_uri(reverse('tap_tables'))
                }
            }
        },
        {
            'schemaID': 'ivo://ivoa.net/std/DALI#examples',
            'interface': {
            'attrs': {
                'xsi:type': 'vr:WebBrowser',
                },
                'accessURL': {
                    'attrs': {
                        'use': 'full'
                    },
                    'text': request.build_absolute_uri(reverse('tap_examples'))
                }
            }
        }
    ]

    return HttpResponse(CapabilitiesRenderer().render(data), content_type="application/xml")

def tables(request):
    serializer = SchemaSerializer(Schema.objects.using('tap').all(), many=True)
    return HttpResponse(TablesetRenderer().render(serializer.data), content_type="application/xml")
