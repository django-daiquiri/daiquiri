from datetime import datetime

from rest_framework.views import APIView
from rest_framework.response import Response

from .renderers import OAIPMHRenderer


class OAIPMHView(APIView):

    renderer_classes = (OAIPMHRenderer, )

    def get(self, request):
        return self.get_response(request, request.GET)

    def post(self, request):
        return self.get_response(request, request.POST)

    def get_response(self, request, params):
        # initialize response and errors array
        self.response = None
        self.errors = []

        # validate keys in params
        for key in params:
            if len(params.getlist(key)) > 1:
                if key == 'verb':
                    self.errors.append(('badVerb', 'Found illegal duplicate of verb'))
                else:
                    self.errors.append(('badArgument', 'Found illegal duplicate of argument \'%s\'.' % key))

        verb = params.get('verb')

        if verb is None:
            self.errors.append(('badArgument', 'OAI verb missing'))
        elif verb == 'GetRecord':
            self.get_record(params)
        elif verb == 'Identify':
            self.identify(params)
        elif verb == 'ListIdentifiers':
            self.list_identifiers(params)
        elif verb == 'ListMetadataFormats':
            self.list_metadata_formats(params)
        elif verb == 'ListRecords':
            self.list_records(params)
        elif verb == 'ListSets':
            self.list_sets(params)
        else:
            self.errors.append(('badVerb', 'Illegal OAI verb'))

        return Response({
            'response_date': datetime.utcnow().replace(microsecond=0).isoformat() + 'Z',
            'request': request.build_absolute_uri(request.path),
            'params': params,
            'errors': self.errors,
            'response': self.response
        })

    def get_record(self, params):
        pass

    def identify(self, params):
        pass

    def list_identifiers(self, params):
        if 'metadataPrefix' not in params:
            self.errors.append(('badArgument', 'Verb \'ListIdentifiers\', argument \'metadataPrefix\' required but not supplied.'))
        else:
            return []

    def list_metadata_formats(self, params):
        pass

    def list_records(self, params):
        pass

    def list_sets(self, params):
        pass
