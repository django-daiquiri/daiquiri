from datetime import datetime
from urllib.parse import quote, unquote

from django.apps import apps
from django.conf import settings
from django.http.request import QueryDict
from django.utils.http import urlencode

from rest_framework.response import Response
from rest_framework.views import APIView

from .adapter import OaiAdapter
from .models import Record
from .renderers import OaiRenderer
from .utils import get_metadata_format, get_renderer


class OaiView(APIView):

    def get(self, request):
        return self.get_response(request, request.GET)

    def post(self, request):
        return self.get_response(request, request.POST)

    def get_response(self, request, query_dict):
        # initialize response and errors array
        self.response = None
        self.errors = []

        verb, arguments = self.get_verb_and_arguments(query_dict)

        if verb is None:
            self.errors.append(('badArgument', 'OAI verb missing'))
        elif verb == 'GetRecord':
            self.get_record(arguments)
        elif verb == 'Identify':
            self.identify(arguments)
        elif verb == 'ListIdentifiers':
            self.list_records(arguments, metadata=False)
        elif verb == 'ListMetadataFormats':
            self.list_metadata_formats(arguments)
        elif verb == 'ListRecords':
            self.list_records(arguments)
        elif verb == 'ListSets':
            self.list_sets(arguments)
        else:
            self.errors.append(('badVerb', 'Illegal OAI verb'))

        if self.response is not None and 'metadataPrefix' in self.response:
            renderer = get_renderer(self.response['metadataPrefix'])
        else:
            renderer = OaiRenderer()

        request.accepted_renderer = renderer
        request.accepted_media_type = renderer.media_type

        return Response({
            'responseDate': datetime.utcnow().replace(microsecond=0).isoformat() + 'Z',
            'baseUrl': request.build_absolute_uri(request.path),
            'verb': verb,
            'arguments': arguments,
            'errors': self.errors,
            'response': self.response
        })

    def get_verb_and_arguments(self, query_dict):
        # validate keys in params
        arguments = {}
        for key in query_dict:
            if len(query_dict.getlist(key)) > 1:
                if key == 'verb':
                    self.errors.append(('badVerb', 'Found illegal duplicate of verb'))
                else:
                    self.errors.append(('badArgument', f'Found illegal duplicate of argument \'{key}\'.'))
            else:
                arguments[key] = query_dict.get(key)

        verb = arguments.pop('verb', None)

        return verb, arguments

    def identify(self, arguments):
        self.validate_illegal_arguments(arguments, [])

        if self.errors:
            return

        adapter = OaiAdapter()

        earliest_record = Record.objects.order_by('datestamp').first()

        self.response = {
            'repository_name': settings.SITE_IDENTIFIER,
            'admin_email': settings.SITE_CONTACT['email'],
            'earliest_datestamp': earliest_record.datestamp if earliest_record else None,
            'deleted_record': settings.OAI_DELETED_RECORD,
            'identifier': {
                'scheme': adapter.identifier_schema,
                'repository_identifier': adapter.identifier_repository,
                'delimiter': adapter.identifier_delimiter,
                'sample_identifier': adapter.get_sample_identifier()
            },
            'registry': self.get_registry()
        }

    def get_record(self, arguments):
        self.validate_illegal_arguments(arguments, ['identifier', 'metadataPrefix'])
        self.validate_identifier(arguments)
        self.validate_metadata_prefix(arguments)

        if self.errors:
            return

        records = Record.objects.filter(identifier=arguments['identifier'])

        if not records.exists():
            self.errors.append(('idDoesNotExist', 'No item found with this identifier'))
            return

        try:
            record = records.get(metadata_prefix=arguments['metadataPrefix'])
        except Record.DoesNotExist:
            self.errors.append(
                ('cannotDisseminateFormat', 'No item found for this identifier with this metadataPrefix')
            )
            return

        self.response = {
            'header': self.get_header(record),
            'metadata': self.get_metadata(record),
            'metadataPrefix': arguments['metadataPrefix']
        }

    def list_metadata_formats(self, arguments):
        self.validate_illegal_arguments(arguments, ['identifier'])

        if self.errors:
            return

        if 'identifier' in arguments:
            records = Record.objects.filter(identifier=arguments['identifier'])

            if not records.exists():
                self.errors.append(('idDoesNotExist', 'No item found with this identifier'))
                return

            else:
                self.response = [get_metadata_format(record.metadata_prefix) for record in records]

        else:
            self.response = settings.OAI_METADATA_FORMATS

    def list_records(self, arguments, metadata=True):
        self.validate_illegal_arguments(arguments, ['from', 'until', 'metadataPrefix', 'set', 'resumptionToken'])
        arguments = self.validate_resumption_token(arguments)

        if self.errors:
            return

        from_date = self.validate_date('from', arguments)
        until_date = self.validate_date('until', arguments)
        set_spec = self.validate_set(arguments)
        self.validate_metadata_prefix(arguments)

        if self.errors:
            return

        records = Record.objects.filter(metadata_prefix=arguments['metadataPrefix'])

        if set_spec:
            records = records.filter(set_spec=set_spec)

        if from_date:
            records = records.filter(datestamp__gte=from_date)

        if until_date:
            records = records.filter(datestamp__lte=until_date)

        count = records.count()
        if count >= settings.OAI_PAGE_SIZE:
            start = int(arguments.pop('start', '0'))
            stop = start + settings.OAI_PAGE_SIZE

            records = records[start:stop]

            if stop < count:
                resumption_token = {
                    'completeListSize': count,
                    'cursor': start,
                    'token': quote(urlencode(dict(start=stop, **arguments)))
                }
            else:
                resumption_token = False

        else:
            resumption_token = False

        if not records.exists():
            self.errors.append(('noRecordsMatch', 'No items found'))
            return

        self.response = {
            'items': [
                {
                    'header': self.get_header(record),
                    'metadata': self.get_metadata(record) if metadata else None
                } for record in records
            ],
            'resumptionToken': resumption_token,
            'metadataPrefix': arguments['metadataPrefix']
        }

    def list_sets(self, arguments):
        self.validate_illegal_arguments(arguments, ['resumptionToken'])
        if settings.OAI_SETS:
            # need to be ordered, see note in
            # https://docs.djangoproject.com/en/3.0/ref/models/querysets/#django.db.models.query.QuerySet.distinct
            oai_sets = Record.objects.order_by('set_spec').values('set_spec').distinct('set_spec')
            self.response = {
                'oai_sets': [
                    {
                        'setSpec': oai_set['set_spec'],
                        'setName': oai_set['set_spec'],
                        'setDescription': None
                    } for oai_set in oai_sets
                ]
            }
        else:
            self.errors.append(('noSetHierarchy', 'This repository does not support sets'))

    def validate_illegal_arguments(self, arguments, valid_keys):
        for key in arguments:
            if key not in valid_keys:
                self.errors.append(('badArgument', f'Found illegal argument \'{key}\'.'))
        else:
            return None

    def validate_date(self, key, arguments):
        if key in arguments:
            try:
                return datetime.strptime(arguments[key], '%Y-%m-%dT%H:%M:%SZ').date()
            except ValueError:
                self.errors.append(('badArgument', f'Argument \'{key}\' does not match format YYYY-MM-DDThh:mm:ssZ'))
        else:
            return None

    def validate_resumption_token(self, arguments):
        if 'resumptionToken' in arguments:
            resumption_token = arguments.pop('resumptionToken')
            if arguments:
                self.errors.append(('badArgument', 'resumptionToken is an exclusive argument.'))

            query_dict = QueryDict(query_string=unquote(resumption_token), mutable=False)
            verb, arguments = self.get_verb_and_arguments(query_dict)
            if 'start' not in arguments:
                self.errors.append(('badResumptionToken', 'The value of the resumptionToken argument is invalid.'))

        return arguments

    def validate_set(self, arguments):
        if 'set' in arguments:
            if not settings.OAI_SETS:
                self.errors.append(('noSetHierarchy', 'This repository does not support sets'))
            else:
                return arguments['set']
        else:
            return None

    def validate_identifier(self, arguments):
        if 'identifier' not in arguments:
            self.errors.append(('badArgument', 'Argument \'identifier\' required but not supplied.'))

    def validate_metadata_prefix(self, arguments):
        valid_prefixes = [metadata_format['prefix'] for metadata_format in settings.OAI_METADATA_FORMATS]

        if 'metadataPrefix' not in arguments:
            self.errors.append(('badArgument', 'Argument \'metadataPrefix\' required but not supplied.'))
        elif arguments['metadataPrefix'] not in valid_prefixes:
            self.errors.append((
                'cannotDisseminateFormat',
                'The metadataPrefix \'{}\' is not supported by this repository.'.format(arguments['metadataPrefix'])
            ))

    def get_header(self, record):
        return {
            'identifier': record.identifier,
            'datestamp': record.datestamp,
            'deleted': record.deleted,
            'setSpec': [record.set_spec]
        }

    def get_metadata(self, record):
        if record.deleted:
            return None
        else:
            adapter = OaiAdapter()
            resource = adapter.get_resource(record)
            serializer_class = adapter.get_serializer_class(record.metadata_prefix, record.resource_type)
            if serializer_class is not None:
                serializer = serializer_class(instance=resource, context={
                    'request': self.request
                })
            else:
                raise RuntimeError(f'Could not determine serializer_class for record {record.identifier}')
            return serializer.data

    def get_registry(self):
        if apps.is_installed('daiquiri.registry'):
            from daiquiri.registry.vo import get_resource
            return get_resource()
