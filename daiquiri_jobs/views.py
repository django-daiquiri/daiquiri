from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import get_object_or_404


from rest_framework import viewsets
from rest_framework.decorators import detail_route
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from rest_framework.parsers import FormParser, JSONParser

from .models import Job
from .serializers import JobsSerializer, JobSerializer
from .utils import UWSRenderer, UWSParser, UWSException


class JobsViewSet(viewsets.ModelViewSet):
    PHASE_RUN = 'RUN'
    PHASE_ABORT = 'ABORT'

    queryset = Job.objects.all()
    renderer_classes = (BrowsableAPIRenderer, JSONRenderer, UWSRenderer)
    parser_classes = (FormParser, JSONParser, UWSParser)

    def get_serializer_class(self):
        if self.action == 'list':
            return JobsSerializer
        else:
            return JobSerializer

    def _redirect_to_job_303(self, job):
        url = reverse('uws:job-detail', args=[job.id])
        return HttpResponseRedirect(url, status=303)

    @detail_route(methods=['get', 'post'])
    def phase(self, request, pk):
        job = get_object_or_404(Job, pk=pk)

        if request.method == 'POST':
            phase = request.POST.get('PHASE')

            if phase == self.PHASE_RUN:
                try:
                    job.run()
                    return self._redirect_to_job_303(job)
                except UWSException:
                    pass
            elif phase == self.PHASE_ABORT:
                try:
                    job.abort()
                    return self._redirect_to_job_303(job)
                except UWSException:
                    pass

            return HttpResponseBadRequest()
        else:
            return HttpResponse(job.get_phase_str())

    @detail_route(methods=['get'])
    def executionduration(self, request, pk):
        job = get_object_or_404(Job, pk=pk)
        return HttpResponse(job.execution_duration if job.execution_duration else '')

    @detail_route(methods=['get'])
    def destruction(self, request, pk):
        job = get_object_or_404(Job, pk=pk)
        return HttpResponse(job.destruction_time if job.destruction_time else '')

    @detail_route(methods=['get'])
    def error(self, request, pk):
        job = get_object_or_404(Job, pk=pk)
        return HttpResponse(job.error if job.error else '')

    @detail_route(methods=['get'])
    def quote(self, request, pk):
        job = get_object_or_404(Job, pk=pk)
        return HttpResponse(job.destruction_time if job.destruction_time else '')

    @detail_route(methods=['get'])
    def owner(self, request, pk):
        job = get_object_or_404(Job, pk=pk)
        return HttpResponse(job.owner.username)
