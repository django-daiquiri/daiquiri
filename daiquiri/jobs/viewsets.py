from django.http import HttpResponse, FileResponse
from django.urls import reverse

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.parsers import FormParser
from rest_framework.exceptions import ValidationError
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.decorators import detail_route

from daiquiri.core.responses import HttpResponseSeeOther
from daiquiri.core.utils import get_client_ip

from .models import Job
from .serializers import (
    JobListSerializer,
    JobRetrieveSerializer,
    JobUpdateSerializer,
    SyncJobSerializer,
    AsyncJobSerializer
)
from .renderers import UWSRenderer, UWSErrorRenderer
from .filters import UWSFilterBackend
from .utils import get_job_url, get_job_results


class JobViewSet(viewsets.GenericViewSet):

    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)
    parser_classes = (FormParser, )

    parameter_map = {}

    def rewrite_exception(self, exception):
        detail = {}
        for field, field_errors in exception.detail.items():
            parameter = dict(map(reversed, self.parameter_map.items()))[field]
            detail[parameter] = field_errors
        return detail


class SyncJobViewSet(JobViewSet):

    serializer_class = SyncJobSerializer

    renderer_classes = (UWSErrorRenderer, )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # create the job objects
        job = self.get_queryset().model(
            job_type=Job.JOB_TYPE_SYNC,
            owner=(None if self.request.user.is_anonymous() else self.request.user),
            response_format=serializer.data.get('RESPONSEFORMAT'),
            max_records=serializer.data.get('MAXREC'),
            run_id=serializer.data.get('RUNID'),
            client_ip=get_client_ip(self.request)
        )

        # add parameters to the job object
        for parameter, model_field in self.parameter_map.items():
            value = serializer.data.get(parameter)
            if value is not None:
                setattr(job, model_field, value)

        try:
            job.process()
        except ValidationError as e:
            raise ValidationError(self.rewrite_exception(e))

        job.save()
        job.run(sync=True)

        # reload the job from the database since job.run() doesn't work on the same job object
        job = self.get_queryset().get(pk=job.pk)

        if job.phase == job.PHASE_COMPLETED:
            return FileResponse(job.stream(job.response_format), content_type=job.formats[job.response_format])
        else:
            return Response(job.error_summary, content_type='application/xml')


class AsyncJobViewSet(JobViewSet):

    serializer_class = AsyncJobSerializer
    renderer_classes = (UWSErrorRenderer, )
    filter_backends = (UWSFilterBackend, )

    def get_success_url(self, job=None):
        if job:
            kwargs = {'pk': job.pk}
        else:
            kwargs = self.kwargs

        return get_job_url(self.request, kwargs=kwargs)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = JobListSerializer(queryset, many=True)
        renderered_data = UWSRenderer().render(serializer.data, renderer_context=self.get_renderer_context())
        return HttpResponse(renderered_data, content_type=UWSRenderer.media_type)

    def retrieve(self, request, *args, **kwargs):
        job = self.get_object()
        serializer = JobRetrieveSerializer(job, context={'request': request})
        renderered_data = UWSRenderer().render(serializer.data, renderer_context=self.get_renderer_context())
        return HttpResponse(renderered_data, content_type=UWSRenderer.media_type)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # create the job objects
        job = self.get_queryset().model(
            job_type=Job.JOB_TYPE_ASYNC,
            owner=(None if self.request.user.is_anonymous() else self.request.user),
            response_format=serializer.data.get('RESPONSEFORMAT'),
            max_records=serializer.data.get('MAXREC'),
            run_id=serializer.data.get('RUNID'),
            client_ip=get_client_ip(self.request)
        )

        # add parameters to the job object
        for parameter, model_field in self.parameter_map.items():
            value = serializer.data.get(parameter)
            if value is not None:
                setattr(job, model_field, value)

        try:
            job.process()
        except ValidationError as e:
            raise ValidationError(self.rewrite_exception(e))

        job.save()

        if serializer.data.get('PHASE') == job.PHASE_RUN:
            job.run()

        return HttpResponseSeeOther(self.get_success_url(job))

    def update(self, request, *args, **kwargs):
        self.get_object()  # necessary to check permissions

        serializer = JobUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if 'ACTION' in serializer.data:
            if serializer.data['ACTION'] == 'DELETE':
                return self.destroy(self, request)
            else:
                raise ValidationError({
                    'PHASE': 'Unsupported value.'
                })
        else:
            raise ValidationError({
                'ACTION': 'Parameter not found.'
            })

    def destroy(self, request, *args, **kwargs):
        job = self.get_object()
        job.archive()
        return HttpResponseSeeOther(self.get_success_url())

    @detail_route(methods=['get'])
    def results(self, request, pk, key=None):
        job = self.get_object()

        renderered_data = UWSRenderer().render({
            'results': get_job_results(request, job)
        }, renderer_context=self.get_renderer_context())
        return HttpResponse(renderered_data, content_type=UWSRenderer.media_type)

    @detail_route(methods=['get'], url_path='results/(?P<result>[A-Za-z0-9\-]+)', url_name='result')
    def result(self, request, pk, result):
        job = self.get_object()

        if result == 'result':
            return FileResponse(job.stream(job.response_format), content_type=job.formats[job.response_format])
        elif result in job.formats:
            return FileResponse(job.stream(result), content_type=job.formats[result])
        else:
            raise ValidationError({
                'result': 'Unsupported value.'
            })

    @detail_route(methods=['get'])
    def parameters(self, request, pk):
        renderered_data = UWSRenderer().render({
            'parameters': self.get_object().parameters
        }, renderer_context=self.get_renderer_context())
        return HttpResponse(renderered_data, content_type=UWSRenderer.media_type)

    @detail_route(methods=['get', 'post'])
    def destruction(self, request, pk):
        job = self.get_object()

        if request.method == 'GET':
            if job.destruction_time:
                # use the JobUpdateSerializer to create timestamp
                serializer = JobUpdateSerializer({
                    'DESTRUCTION': job.destruction_time
                })

                return HttpResponse(serializer.data['DESTRUCTION'])
            else:
                return HttpResponse()
        else:
            serializer = JobUpdateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            if 'DESTRUCTION' in serializer.data:
                job.destruction_time = serializer.data['DESTRUCTION']
                job.save()
                return HttpResponseSeeOther(self.get_success_url(), status=303)
            else:
                raise ValidationError({
                    'DESTRUCTION': 'Parameter not found.'
                })

    @detail_route(methods=['get', 'post'])
    def executionduration(self, request, pk):
        job = self.get_object()

        if request.method == 'GET':
            return HttpResponse(job.execution_duration)
        else:
            serializer = JobUpdateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            if 'EXECUTIONDURATION' in serializer.data:
                job.execution_duration = serializer.data['EXECUTIONDURATION']
                job.save()
                return HttpResponseSeeOther(self.get_success_url())
            else:
                raise ValidationError({
                    'EXECUTIONDURATION': 'Parameter not found.'
                })

    @detail_route(methods=['get', 'post'])
    def phase(self, request, pk):
        job = self.get_object()

        if request.method == 'GET':
            return HttpResponse(job.phase)
        else:
            serializer = JobUpdateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            if 'PHASE' in serializer.data:
                phase = serializer.data['PHASE']
                if phase == job.PHASE_RUN:
                    try:
                        job.process()
                    except ValidationError as e:
                        raise ValidationError(self.rewrite_exception(e))

                    job.run()
                    return HttpResponseSeeOther(self.get_success_url())

                elif phase == job.PHASE_ABORT:
                    job.abort()
                    return HttpResponseSeeOther(self.get_success_url())

                else:
                    raise ValidationError({
                        'PHASE': 'Unsupported value.'
                    })
            else:
                raise ValidationError({
                    'PHASE': 'Parameter not found.'
                })

    @detail_route(methods=['get'])
    def error(self, request, pk):
        job = self.get_object()
        return Response(job.error_summary, content_type='application/xml') if job.error_summary else HttpResponse()

    @detail_route(methods=['get'])
    def quote(self, request, pk):
        job = self.get_object()
        return HttpResponse(job.quote) if job.quote else HttpResponse()

    @detail_route(methods=['get'])
    def owner(self, request, pk):
        job = self.get_object()
        return HttpResponse(job.owner) if job.owner else HttpResponse()
