from django.http import HttpResponse

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.parsers import FormParser
from rest_framework.exceptions import ValidationError
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication

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
from .renderers import UWSRenderer, ErrorRenderer
from .filters import UWSFilterBackend
from .utils import get_job_url


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

    renderer_classes = (ErrorRenderer, )

    def create_job(self, request, *args, **kwargs):
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
            return HttpResponseSeeOther(self.request.build_absolute_uri(job.result))
        else:
            return Response(job.error_summary, content_type='application/xml')


class AsyncJobViewSet(JobViewSet):

    serializer_class = AsyncJobSerializer
    renderer_classes = (ErrorRenderer, )
    filter_backends = (UWSFilterBackend, )

    def get_success_url(self, job=None):
        if job:
            kwargs = {'pk': job.pk}
        else:
            kwargs = self.kwargs

        return get_job_url(self.request, kwargs=kwargs)

    def list_jobs(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = JobListSerializer(queryset, many=True)
        renderered_data = UWSRenderer().render(serializer.data, renderer_context=self.get_renderer_context())
        return HttpResponse(renderered_data, content_type=UWSRenderer.media_type)

    def retrieve_job(self, request, *args, **kwargs):
        job = self.get_object()
        serializer = JobRetrieveSerializer(job)
        renderered_data = UWSRenderer().render(serializer.data, renderer_context=self.get_renderer_context())
        return HttpResponse(renderered_data, content_type=UWSRenderer.media_type)

    def create_job(self, request, *args, **kwargs):
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

    def update_job(self, request, *args, **kwargs):
        self.get_object()  # necessary to check permissions

        serializer = JobUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if 'ACTION' in serializer.data:
            if serializer.data['ACTION'] == 'DELETE':
                return self.destroy_job(self, request)
            else:
                raise ValidationError({
                    'PHASE': 'Unsupported value.'
                })
        else:
            raise ValidationError({
                'ACTION': 'Parameter not found.'
            })

    def destroy_job(self, request, *args, **kwargs):
        job = self.get_object()
        job.archive()
        return HttpResponseSeeOther(self.get_success_url())

    def get_results(self, request, pk):
        job = self.get_object()

        renderered_data = UWSRenderer().render({
            'results': job.results
        }, renderer_context=self.get_renderer_context())
        return HttpResponse(renderered_data, content_type=UWSRenderer.media_type)

    def get_result(self, request, pk):
        job = self.get_object()
        return HttpResponseSeeOther(job.result)

    def get_parameters(self, request, pk):
        renderered_data = UWSRenderer().render({
            'parameters': self.get_object().parameters
        }, renderer_context=self.get_renderer_context())
        return HttpResponse(renderered_data, content_type=UWSRenderer.media_type)

    def get_destruction(self, request, pk):
        job = self.get_object()

        if job.destruction_time:
            # use the JobUpdateSerializer to create timestamp
            serializer = JobUpdateSerializer({
                'DESTRUCTION': job.destruction_time
            })

            return HttpResponse(serializer.data['DESTRUCTION'])
        else:
            return HttpResponse()

    def set_destruction(self, request, pk):
        job = self.get_object()

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

    def get_executionduration(self, request, pk):
        job = self.get_object()
        return HttpResponse(job.execution_duration)

    def set_executionduration(self, request, pk):
        job = self.get_object()

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

    def get_phase(self, request, pk):
        job = self.get_object()
        return HttpResponse(job.phase)

    def set_phase(self, request, pk):
        job = self.get_object()

        serializer = JobUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if 'PHASE' in serializer.data:
            phase = serializer.data['PHASE']
            if phase == job.PHASE_RUN:
                job.process()
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

    def get_error(self, request, pk):
        job = self.get_object()
        return Response(job.error_summary, content_type='application/xml') if job.error_summary else HttpResponse()

    def get_quote(self, request, pk):
        job = self.get_object()
        return HttpResponse(job.quote) if job.quote else HttpResponse()

    def get_owner(self, request, pk):
        job = self.get_object()
        return HttpResponse(job.owner) if job.owner else HttpResponse()
