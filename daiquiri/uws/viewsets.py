import iso8601

from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.http import HttpResponse

from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.parsers import FormParser
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

from .serializers import (
    UWSJobListSerializer,
    UWSJobRetrieveSerializer,
    UWSJobCreateSerializer,
    UWSJobUpdateSerializer
)
from .renderers import UWSRenderer
from .filters import UWSFilterBackend
from .responses import UWSSuccessRedirect, UWSBadRequest
from .exceptions import UWSException


class UWSJobViewSet(ReadOnlyModelViewSet):

    renderer_classes = (UWSRenderer, )
    parser_classes = (FormParser, )
    filter_backends = (UWSFilterBackend, )

    list_serializer_class = UWSJobListSerializer
    detail_serializer_class = UWSJobRetrieveSerializer
    create_serializer_class = UWSJobCreateSerializer
    update_serializer_class = UWSJobUpdateSerializer

    def get_success_url(self, job=None):
        if job:
            kwargs = {'pk': job.pk}
        else:
            kwargs = self.kwargs

        path = reverse(self.base_name + '-detail', kwargs=kwargs)
        return self.request.build_absolute_uri(path)

    def get_serializer_class(self):
        if self.action == 'list':
            return self.list_serializer_class
        elif self.action == 'create':
            return self.serializer_class
        elif self.action == 'update':
            return self.update_serializer_class
        else:
            return self.detail_serializer_class

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # create the job objects
        job = self.get_queryset().model(owner=(None if self.request.user.is_anonymous() else self.request.user))

        # add parameters to the job object
        for parameter, model_field in self.parameter_map.items():
            setattr(job, model_field, serializer.data.get(parameter))

        try:
            job.clean()
        except ValidationError as e:
            return UWSBadRequest(e)

        job.save()

        if serializer.data.get('PHASE') == job.PHASE_RUN:
            job.run()

        return UWSSuccessRedirect(self.get_success_url(job))

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        job = self.get_object()
        job.clean()

        if serializer.data.get('PHASE') == job.PHASE_RUN:
            job.clean()
            job.run()
            return UWSSuccessRedirect(self.get_success_url())

        elif serializer.data.get('PHASE') == 'DELETE':
            return self.destroy(self, request)
        else:
            return UWSSuccessRedirect(self.get_success_url())

    def destroy(self, request, *args, **kwargs):
        job = self.get_object()
        try:
            job.archive()
            return UWSSuccessRedirect(self.get_success_url())
        except UWSException as e:
            return UWSBadRequest(e)

    def get_results(self, request, pk):
        return Response({
            'results': self.get_object().results
        })

    def get_result(self, request, pk):
        return UWSSuccessRedirect(self.get_object().result)

    def get_parameters(self, request, pk):
        return Response({
            'parameters': self.get_object().parameters
        })

    def get_destruction(self, request, pk):
        job = self.get_object()
        if job.destruction_time:
            return HttpResponse(job.destruction_time)
        else:
            return HttpResponse()

    def post_destruction(self, request, pk):
        job = self.get_object()
        try:
            job.destruction_time = iso8601.parse_date(request.POST.get('DESTRUCTION'))
            job.save()
            return UWSSuccessRedirect(self.get_success_url(), status=303)
        except (TypeError, IntegrityError, ValueError) as e:
            return UWSBadRequest(e)

    def get_executionduration(self, request, pk):
        job = self.get_object()
        if job.execution_duration:
            return HttpResponse(job.execution_duration)
        else:
            return HttpResponse()

    def post_executionduration(self, request, pk):
        job = self.get_object()
        try:
            job.execution_duration = request.POST.get('EXECUTIONDURATION')
            job.save()
            return UWSSuccessRedirect(self.get_success_url(), status=303)
        except (IntegrityError, ValueError) as e:
            return UWSBadRequest(e)

    def get_phase(self, request, pk):
        job = self.get_object()
        return HttpResponse(job.phase)

    def post_phase(self, request, pk):
        job = self.get_object()

        phase = request.POST.get('PHASE')

        if phase == job.PHASE_RUN:
            try:
                job.run()
                return UWSSuccessRedirect(self.get_success_url(), status=303)
            except UWSException as e:
                return UWSBadRequest(e)
        elif phase == job.PHASE_ABORT:
            try:
                job.abort()
                return UWSSuccessRedirect(self.get_success_url(), status=303)
            except UWSException as e:
                return UWSBadRequest(e)
        else:
            return UWSBadRequest('unsupported value for PHASE')

    def get_error(self, request, pk):
        job = self.get_object()
        return HttpResponse(job.error) if job.error else HttpResponse()

    def get_quote(self, request, pk):
        job = self.get_object()
        return HttpResponse(job.quote) if job.quote else HttpResponse()

    def get_owner(self, request, pk):
        job = self.get_object()
        return HttpResponse(job.owner) if job.owner else HttpResponse()
