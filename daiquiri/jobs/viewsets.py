from django.http import FileResponse, HttpResponse

from rest_framework import viewsets
from rest_framework.authentication import BasicAuthentication, SessionAuthentication, TokenAuthentication
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from daiquiri.core.responses import HttpResponseSeeOther
from daiquiri.core.utils import get_client_ip

from .filters import UWSFilterBackend
from .models import Job
from .renderers import UWSErrorRenderer, UWSRenderer
from .serializers import (
    AsyncJobSerializer,
    JobListSerializer,
    JobRetrieveSerializer,
    JobUpdateSerializer,
    SyncJobSerializer,
)
from .utils import get_content_type, get_job_results, get_job_url, get_max_records


class JobViewSet(viewsets.GenericViewSet):

    authentication_classes = (SessionAuthentication, BasicAuthentication, TokenAuthentication)
    parser_classes = (FormParser, MultiPartParser)

    parameter_map = {}

    def rewrite_exception(self, exception):
        detail = {}
        for field, field_errors in exception.detail.items():
            parameter = dict(map(reversed, self.parameter_map.items())).get(field, field.upper())
            detail[parameter] = field_errors
        return detail

    def handle_upload(self, job, upload_string):
        pass


class SyncJobViewSet(JobViewSet):

    serializer_class = SyncJobSerializer

    renderer_classes = (UWSErrorRenderer, )

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.GET)
        serializer.is_valid(raise_exception=True)

        return self.perform_sync_job(request, serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return self.perform_sync_job(request, serializer.validated_data)

    def perform_sync_job(self, request, data):
        maxrec = data.get('MAXREC')
        max_records = get_max_records(request.user)
        if maxrec is not None and maxrec < max_records:
            max_records = maxrec

        # create the job objects
        job = self.get_queryset().model(
            job_type=Job.JOB_TYPE_SYNC,
            owner=(None if self.request.user.is_anonymous else self.request.user),
            response_format=data.get('RESPONSEFORMAT'),
            max_records=max_records,
            run_id=data.get('RUNID'),
            client_ip=get_client_ip(self.request)
        )

        # add parameters to the job object
        for parameter, model_field in self.parameter_map.items():
            value = data.get(parameter)
            if value is not None:
                setattr(job, model_field, value)

        # handle possible uploads
        try:
            self.handle_upload(job, data.get('UPLOAD'))
        except ValueError as e:
            raise ValidationError('Could not parse VOTable') from e

        try:
            job.process()
        except ValidationError as e:
            raise ValidationError(self.rewrite_exception(e)) from e

        return FileResponse(job.run_sync(), content_type='application/xml')
        return FileResponse(job.run_sync(), content_type=job.formats[job.response_format])


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
        rendered_data = UWSRenderer().render(serializer.data, renderer_context=self.get_renderer_context())
        return HttpResponse(rendered_data, content_type=get_content_type(request, UWSRenderer))

    def retrieve(self, request, *args, **kwargs):
        job = self.get_object()
        serializer = JobRetrieveSerializer(job, context={'request': request})
        rendered_data = UWSRenderer().render(serializer.data, renderer_context=self.get_renderer_context())
        return HttpResponse(rendered_data, content_type=get_content_type(request, UWSRenderer))

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        maxrec = serializer.validated_data.get('MAXREC')
        max_records = get_max_records(request.user)
        if maxrec is not None and maxrec < max_records:
            max_records = maxrec

        # create the job objects
        job = self.get_queryset().model(
            job_type=Job.JOB_TYPE_ASYNC,
            owner=(None if self.request.user.is_anonymous else self.request.user),
            response_format=serializer.validated_data.get('RESPONSEFORMAT'),
            max_records=max_records,
            # uploads=handle_uploads(request, serializer.validated_data.get('UPLOAD'), self.get_upload_directory()),
            run_id=serializer.validated_data.get('RUNID'),
            client_ip=get_client_ip(self.request)
        )

        # add parameters to the job object
        for parameter, model_field in self.parameter_map.items():
            value = serializer.validated_data.get(parameter)
            if value is not None:
                setattr(job, model_field, value)

        # handle possible uploads
        self.handle_upload(job, serializer.validated_data.get('UPLOAD'))

        try:
            job.process()
        except ValidationError as e:
            raise ValidationError(self.rewrite_exception(e)) from e

        job.save()

        if serializer.validated_data.get('PHASE') == job.PHASE_RUN:
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

    @action(detail=True, methods=['get'])
    def results(self, request, pk, key=None):
        job = self.get_object()

        rendered_data = UWSRenderer().render({
            'results': get_job_results(request, job)
        }, renderer_context=self.get_renderer_context())
        return HttpResponse(rendered_data, content_type=get_content_type(request, UWSRenderer))

    @action(detail=True, methods=['get'], url_path=r'results/(?P<result>[A-Za-z0-9\-]+)', url_name='result')
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

    @action(detail=True, methods=['get'])
    def parameters(self, request, pk):
        rendered_data = UWSRenderer().render({
            'parameters': self.get_object().parameters
        }, renderer_context=self.get_renderer_context())
        return HttpResponse(rendered_data, content_type=get_content_type(request, UWSRenderer))

    @action(detail=True, methods=['get', 'post'])
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

    @action(detail=True, methods=['get', 'post'])
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

    @action(detail=True, methods=['get', 'post'])
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
                        raise ValidationError(self.rewrite_exception(e)) from e

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

    @action(detail=True, methods=['get'])
    def error(self, request, pk):
        job = self.get_object()
        return Response(job.error_summary, content_type='application/xml') if job.error_summary else HttpResponse()

    @action(detail=True, methods=['get'])
    def quote(self, request, pk):
        job = self.get_object()
        return HttpResponse(job.quote) if job.quote else HttpResponse()

    @action(detail=True, methods=['get'])
    def owner(self, request, pk):
        job = self.get_object()
        return HttpResponse(job.owner) if job.owner else HttpResponse()
