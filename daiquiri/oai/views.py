from datetime import datetime, date

from django.conf import settings
from django.contrib.sites.models import Site

from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Record
from .renderers import OaiRenderer


class OaiView(APIView):

    renderer_classes = (OaiRenderer, )

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
            self.list_identifiers(arguments)
        elif verb == 'ListMetadataFormats':
            self.list_metadata_formats(arguments)
        elif verb == 'ListRecords':
            self.list_records(arguments)
        elif verb == 'ListSets':
            self.list_sets(arguments)
        else:
            self.errors.append(('badVerb', 'Illegal OAI verb'))

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
                    self.errors.append(('badArgument', 'Found illegal duplicate of argument \'%s\'.' % key))
            else:
                arguments[key] = query_dict.get(key)

        verb = arguments.pop('verb', None)

        return verb, arguments

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
            self.errors.append(('cannotDisseminateFormat', 'No item found for this identifier with this metadataPrefix'))
            return

        self.response = {
            'identifier': record.identifier,
            'datestamp': record.datestamp,
            'metadata': None
        }

    def identify(self, arguments):
        self.validate_illegal_arguments(arguments, [])

        if self.errors:
            return

        earliest_record = Record.objects.order_by('datestamp').first()

        self.response = {
            'repositoryName': Site.objects.get_current(),
            'adminEmails': settings.OAI_ADMIN_EMAILS,
            'earliestDatestamp': earliest_record.datestamp if earliest_record else None,
            'deletedRecord': settings.OAI_DELETED_RECORD,
            'granularity': settings.OAI_GRANULARITY
        }

    def list_identifiers(self, arguments):
        self.validate_illegal_arguments(arguments, ['from', 'until', 'metadataPrefix', 'set', 'resumptionToken'])
        from_date = self.validate_date('from', arguments)
        until_date = self.validate_date('until', arguments)
        self.validate_metadata_prefix(arguments)
        self.validate_resumption_token(arguments)
        self.validate_set(arguments)

        if self.errors:
            return

        records = Record.objects.filter(metadata_prefix=arguments['metadataPrefix'])

        if from_date:
            records = records.filter(datestamp__gte=from_date)

        if until_date:
            records = records.filter(datestamp__lte=until_date)

        if not records.exists():
            self.errors.append(('noRecordsMatch', 'No items found'))
            return

        self.response = [{
            'identifier': record.identifier,
            'datestamp': record.datestamp,
        } for record in records]

    def list_metadata_formats(self, arguments):
        self.validate_illegal_arguments(arguments, ['identifier'])

        if self.errors:
            return

        if 'identifier' in arguments:
            records = Record.objects.filter(identifier=arguments['identifier'])

            if not records.exists():
                self.errors.append(('idDoesNotExist', 'No item found with this identifier'))
                return

                self.response = [{
                    'metadataPrefix': record.metadata_prefix
                } for record in records]

            else:
                self.response = [
                    next(metadata_format for metadata_format in settings.OAI_METADATA_FORMATS
                         if metadata_format['prefix'] == record.metadata_prefix)
                    for record in records
                ]

        else:
            self.response = settings.OAI_METADATA_FORMATS

    def list_records(self, arguments):
        self.validate_illegal_arguments(arguments, ['from', 'until', 'metadataPrefix', 'set', 'resumptionToken'])
        from_date = self.validate_date('from', arguments)
        until_date = self.validate_date('until', arguments)
        self.validate_metadata_prefix(arguments)
        self.validate_resumption_token(arguments)
        self.validate_set(arguments)

        if self.errors:
            return

        records = Record.objects.filter(metadata_prefix=arguments['metadataPrefix'])

        if from_date:
            records = records.filter(datestamp__gte=from_date)

        if until_date:
            records = records.filter(datestamp__lte=until_date)

        if not records.exists():
            self.errors.append(('noRecordsMatch', 'No items found'))
            return

        self.response = [{
            'identifier': record.identifier,
            'datestamp': record.datestamp,
            'metadata': None
        } for record in records]

    def list_sets(self, arguments):
        self.validate_illegal_arguments(arguments, ['resumptionToken'])
        self.errors.append(('noSetHierarchy', 'This repository does not support sets'))

    def validate_illegal_arguments(self, arguments, valid_keys):
        for key in arguments:
            if key not in valid_keys:
                self.errors.append(('badArgument', 'Found illegal argument \'%s\'.' % key))
        else:
            return None

    def validate_date(self, key, arguments):
        if key in arguments:
            try:
                return datetime.strptime(arguments[key], '%Y-%m-%d').date()
            except ValueError:
                self.errors.append(('badArgument', 'Argument \'%s\' does not match format YYYY-MM-DD' % key))
        else:
            return None

    def validate_resumption_token(self, arguments):
        if 'resumptionToken' in arguments:
            self.errors.append(('badResumptionToken', 'This repository does not support resumption tokens'))

    def validate_set(self, arguments):
        if 'set' in arguments:
            self.errors.append(('noSetHierarchy', 'This repository does not support sets'))

    def validate_identifier(self, arguments):
        if 'identifier' not in arguments:
            self.errors.append(('badArgument', 'Argument \'identifier\' required but not supplied.'))

    def validate_metadata_prefix(self, arguments):
        valid_prefixes = [metadata_format['prefix'] for metadata_format in settings.OAI_METADATA_FORMATS]

        if 'metadataPrefix' not in arguments:
            self.errors.append(('badArgument', 'Argument \'metadataPrefix\' required but not supplied.'))
        elif arguments['metadataPrefix'] not in valid_prefixes:
            self.errors.append((
                'cannotDisseminateFormat', 'The metadataPrefix \'%s\' is not supported by this repository.' % arguments['metadataPrefix']
            ))
