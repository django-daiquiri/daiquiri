from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.http import HttpResponse

from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.decorators import detail_route
from rest_framework.parsers import FormParser
from rest_framework.response import Response

import iso8601

from .renderers import UWSRenderer
from .filters import UWSFilterBackend
from .utils import UWSSuccessRedirect, UWSBadRequest
from .exceptions import UWSException


class UWSViewSet(ReadOnlyModelViewSet):
    PHASE_RUN = 'RUN'
    PHASE_ABORT = 'ABORT'

    renderer_classes = (UWSRenderer, )
    parser_classes = (FormParser, )
    filter_backends = (UWSFilterBackend, )

    def get_success_url(self):
        return reverse(self.detail_url_name, kwargs=self.kwargs)

    def get_serializer_class(self):
        if self.action == 'list':
            return self.list_serializer_class
        else:
            return self.detail_serializer_class

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        try:
            obj.archive()
            return UWSSuccessRedirect(self.get_success_url())
        except UWSException as e:
            return UWSBadRequest(e)

    @detail_route(methods=['get'])
    def results(self, request, pk):
        return Response({
            'results': self.get_object().results
        })

    @detail_route(methods=['get'])
    def parameters(self, request, pk):
        return Response({
            'parameters': self.get_object().parameters
        })

    @detail_route(methods=['get', 'post'])
    def destruction(self, request, pk):
        obj = self.get_object()
        if request.method == 'POST':
            try:
                obj.destruction_time = iso8601.parse_date(request.POST.get('DESTRUCTION'))
                obj.save()
                return UWSSuccessRedirect(self.get_success_url(), status=303)
            except (TypeError, IntegrityError, ValueError) as e:
                return UWSBadRequest(e)
        else:
            if obj.destruction_time:
                return HttpResponse(obj.destruction_time)
            else:
                return HttpResponse()

    @detail_route(methods=['get', 'post'])
    def executionduration(self, request, pk):
        obj = self.get_object()

        if request.method == 'POST':
            try:
                obj.execution_duration = request.POST.get('EXECUTIONDURATION')
                obj.save()
                return UWSSuccessRedirect(self.get_success_url(), status=303)
            except (IntegrityError, ValueError) as e:
                return UWSBadRequest(e)
        else:
            if obj.execution_duration:
                return HttpResponse(obj.execution_duration)
            else:
                return HttpResponse()

    @detail_route(methods=['get', 'post'])
    def phase(self, request, pk):
        obj = self.get_object()

        if request.method == 'POST':
            phase = request.POST.get('PHASE')

            if phase == self.PHASE_RUN:
                try:
                    obj.run()
                    return UWSSuccessRedirect(self.get_success_url(), status=303)
                except UWSException as e:
                    return UWSBadRequest(e)
            elif phase == self.PHASE_ABORT:
                try:
                    obj.abort()
                    return UWSSuccessRedirect(self.get_success_url(), status=303)
                except UWSException as e:
                    return UWSBadRequest(e)
            else:
                return UWSBadRequest('unsupported value for PHASE')
        else:
            return HttpResponse(obj.phase)

    @detail_route(methods=['get'])
    def error(self, request, pk):
        obj = self.get_object()
        return HttpResponse(obj.error) if obj.error else HttpResponse()

    @detail_route(methods=['get'])
    def quote(self, request, pk):
        obj = self.get_object()
        return HttpResponse(obj.quote) if obj.quote else HttpResponse()

    @detail_route(methods=['get'])
    def owner(self, request, pk):
        obj = self.get_object()
        return HttpResponse(obj.owner)
