import iso8601

from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.http import HttpResponse

from rest_framework import viewsets
from rest_framework.parsers import FormParser
from rest_framework.exceptions import ValidationError, NotFound

from daiquiri.core.responses import HttpResponseSeeOther

from .serializers import (
    JobListSerializer,
    JobRetrieveSerializer,
    JobUpdateSerializer,
    SyncJobSerializer,
    AsyncJobSerializer
)
from .renderers import UWSRenderer, ErrorRenderer
from .filters import UWSFilterBackend


class JobViewSet(viewsets.GenericViewSet):

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
        job = self.get_queryset().model(owner=(None if self.request.user.is_anonymous() else self.request.user))

        # add parameters to the job object
        for parameter, model_field in self.parameter_map.items():
            setattr(job, model_field, serializer.data.get(parameter))

        try:
            job.clean()
        except ValidationError as e:
            raise ValidationError(self.rewrite_exception(e))

        job.save()
        job.run(sync=True)

        if serializer.data.get('PHASE') == job.PHASE_RUN:
            job.run()

        # reload the job from the database since job.run() doesn't work on the same job object
        job = self.get_queryset().get(pk=job.pk)

        return HttpResponseSeeOther(self.request.build_absolute_uri(job.result))


class AsyncJobViewSet(JobViewSet):

    serializer_class = AsyncJobSerializer
    renderer_classes = (ErrorRenderer, )
    filter_backends = (UWSFilterBackend, )

    def get_success_url(self, job=None):
        if job:
            kwargs = {'pk': job.pk}
        else:
            kwargs = self.kwargs

        base_name = self.request.resolver_match.url_name.rsplit('-', 1)[0]
        path = reverse(base_name + '-detail', kwargs=kwargs)
        return self.request.build_absolute_uri(path)

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
        job = self.get_queryset().model(owner=(None if self.request.user.is_anonymous() else self.request.user))

        # add parameters to the job object
        for parameter, model_field in self.parameter_map.items():
            setattr(job, model_field, serializer.data.get(parameter))

        try:
            job.clean()
        except ValidationError as e:
            raise ValidationError(self.rewrite_exception(e))

        job.save()

        if serializer.data.get('PHASE') == job.PHASE_RUN:
            job.run()

        return HttpResponseSeeOther(self.get_success_url(job))

    def update_job(self, request, *args, **kwargs):
        serializer = JobUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if serializer.data.get('PHASE') == 'DELETE':
            return self.destroy(self, request)
        else:
            return HttpResponseSeeOther(self.get_success_url())

    def destroy_job(self, request, *args, **kwargs):
        job = self.get_object()
        job.archive()
        return HttpResponseSeeOther(self.get_success_url())

    def get_results(self, request, pk):
        renderered_data = UWSRenderer().render({
            'results': self.get_object().results
        }, renderer_context=self.get_renderer_context())
        return HttpResponse(renderered_data, content_type=UWSRenderer.media_type)

    def get_result(self, request, pk):
        return HttpResponseSeeOther(self.get_object().result)

    def get_parameters(self, request, pk):
        renderered_data = UWSRenderer().render({
            'parameters': self.get_object().parameters
        }, renderer_context=self.get_renderer_context())
        return HttpResponse(renderered_data, content_type=UWSRenderer.media_type)

    def get_destruction(self, request, pk):
        job = self.get_object()
        if job.destruction_time:
            return HttpResponse(job.destruction_time)
        else:
            return HttpResponse()

    def set_destruction(self, request, pk):
        job = self.get_object()
        try:
            job.destruction_time = iso8601.parse_date(request.POST['DESTRUCTION'])
            job.save()
            return HttpResponseSeeOther(self.get_success_url(), status=303)
        except (TypeError, IntegrityError, ValueError) as e:
            raise ValidationError({
                'DESTRUCTION': 'Unsupported value.'
            })
        except KeyError as e:
            raise ValidationError({
                'DESTRUCTION': 'Parameter not found.'
            })

    def get_executionduration(self, request, pk):
        job = self.get_object()
        if job.execution_duration:
            return HttpResponse(job.execution_duration)
        else:
            return HttpResponse()

    def set_executionduration(self, request, pk):
        job = self.get_object()
        try:
            job.execution_duration = request.POST['EXECUTIONDURATION']
            job.save()
            return HttpResponseSeeOther(self.get_success_url())
        except (IntegrityError, ValueError) as e:
            raise ValidationError({
                'EXECUTIONDURATION': 'Unsupported value.'
            })
        except KeyError as e:
            raise ValidationError({
                'EXECUTIONDURATION': 'Parameter not found.'
            })

    def get_phase(self, request, pk):
        job = self.get_object()
        return HttpResponse(job.phase)

    def set_phase(self, request, pk):
        job = self.get_object()

        phase = request.POST.get('PHASE')
        if phase == job.PHASE_RUN:
            job.clean()
            job.run()
            return HttpResponseSeeOther(self.get_success_url())

        elif phase == job.PHASE_ABORT:
            job.abort()
            return HttpResponseSeeOther(self.get_success_url())

        else:
            raise ValidationError({
                'PHASE': 'Unsupported value.'
            })

    def get_error(self, request, pk):
        job = self.get_object()
        return HttpResponse(job.error) if job.error else HttpResponse()

    def get_quote(self, request, pk):
        job = self.get_object()
        return HttpResponse(job.quote) if job.quote else HttpResponse()

    def get_owner(self, request, pk):
        job = self.get_object()
        return HttpResponse(job.owner) if job.owner else HttpResponse()
