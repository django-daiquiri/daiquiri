import iso8601

from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.http import HttpResponse

from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.parsers import FormParser
from rest_framework.response import Response

from daiquiri.jobs.models import Job

from .serializers import JobsSerializer, JobSerializer
from .renderers import UWSRenderer
from .filters import UWSFilterBackend
from .utils import UWSSuccessRedirect, UWSBadRequest
from .exceptions import UWSException
from .settings import PHASE_RUN, PHASE_ABORT, PHASE_PENDING


class UWSViewSet(ReadOnlyModelViewSet):

    renderer_classes = (UWSRenderer, )
    parser_classes = (FormParser, )
    filter_backends = (UWSFilterBackend, )

    job_type = None

    def get_success_url(self, pk=None):
        if pk:
            kwargs = {'pk': pk}
        else:
            kwargs = self.kwargs

        return reverse(self.detail_url_name, kwargs=kwargs)

    def get_serializer_class(self):
        if self.action == 'list':
            return self.list_serializer_class
        else:
            return self.detail_serializer_class

    def create(self, request, *args, **kwargs):
        if not self.job_type:
            return UWSBadRequest('job creation is forbidden on this ressource')

        if request.user.is_authenticated():
            owner = request.user
        else:
            owner = None

        obj = self.get_queryset().model(
            owner=owner,
            phase=PHASE_PENDING,
            job_type=self.job_type
        )
        obj.save()

        if request.GET.get('PHASE') == PHASE_RUN:
            try:
                obj.run()
            except UWSException as e:
                return UWSBadRequest(e)
        return UWSSuccessRedirect(self.get_success_url(obj.pk))

    def update(self, request, *args, **kwargs):
        if request.POST.get('ACTION') == 'DELETE':
            return self.destroy(self, request)
        else:
            # TODO: update parameters
            return UWSSuccessRedirect(self.get_success_url())

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        try:
            obj.archive()
            return UWSSuccessRedirect(self.get_success_url())
        except UWSException as e:
            return UWSBadRequest(e)

    def get_results(self, request, pk):
        return Response({
            'results': self.get_object().results
        })

    def get_parameters(self, request, pk):
        return Response({
            'parameters': self.get_object().parameters
        })

    def get_destruction(self, request, pk):
        obj = self.get_object()
        if obj.destruction_time:
            return HttpResponse(obj.destruction_time)
        else:
            return HttpResponse()

    def post_destruction(self, request, pk):
        obj = self.get_object()
        try:
            obj.destruction_time = iso8601.parse_date(request.POST.get('DESTRUCTION'))
            obj.save()
            return UWSSuccessRedirect(self.get_success_url(), status=303)
        except (TypeError, IntegrityError, ValueError) as e:
            return UWSBadRequest(e)

    def get_executionduration(self, request, pk):
        obj = self.get_object()
        if obj.execution_duration:
            return HttpResponse(obj.execution_duration)
        else:
            return HttpResponse()

    def post_executionduration(self, request, pk):
        obj = self.get_object()
        try:
            obj.execution_duration = request.POST.get('EXECUTIONDURATION')
            obj.save()
            return UWSSuccessRedirect(self.get_success_url(), status=303)
        except (IntegrityError, ValueError) as e:
            return UWSBadRequest(e)

    def get_phase(self, request, pk):
        obj = self.get_object()
        return HttpResponse(obj.phase)

    def post_phase(self, request, pk):
        obj = self.get_object()

        phase = request.POST.get('PHASE')

        if phase == PHASE_RUN:
            try:
                obj.run()
                return UWSSuccessRedirect(self.get_success_url(), status=303)
            except UWSException as e:
                return UWSBadRequest(e)
        elif phase == PHASE_ABORT:
            try:
                obj.abort()
                return UWSSuccessRedirect(self.get_success_url(), status=303)
            except UWSException as e:
                return UWSBadRequest(e)
        else:
            return UWSBadRequest('unsupported value for PHASE')

    def get_error(self, request, pk):
        obj = self.get_object()
        return HttpResponse(obj.error) if obj.error else HttpResponse()

    def get_quote(self, request, pk):
        obj = self.get_object()
        return HttpResponse(obj.quote) if obj.quote else HttpResponse()

    def get_owner(self, request, pk):
        obj = self.get_object()
        return HttpResponse(obj.owner)


class JobsViewSet(UWSViewSet):
    queryset = Job.objects.all()
    list_serializer_class = JobsSerializer
    detail_serializer_class = JobSerializer


class QueryJobsViewSet(JobsViewSet):
    detail_url_name = 'uwsquery-detail'
    job_type = Job.JOB_TYPE_QUERY
