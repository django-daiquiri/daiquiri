from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from rest_framework import viewsets
from rest_framework.decorators import detail_route

from .models import Job
from .serializers import JobsSerializer, JobSerializer
from .renderers import JobRenderer


class JobsViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    renderer_classes = (JobRenderer,)

    def get_serializer_class(self):
        if self.action == 'list':
            return JobsSerializer
        else:
            return JobSerializer

    @detail_route(methods=['get'])
    def phase(self, request, pk):
        job = get_object_or_404(Job, pk=pk)
        return HttpResponse(job.get_phase_str())

    @detail_route(methods=['get'])
    def executionduration(self, request, pk):
        job = get_object_or_404(Job, pk=pk)
        return HttpResponse(job.execution_duration)

    @detail_route(methods=['get'])
    def destruction(self, request, pk):
        job = get_object_or_404(Job, pk=pk)
        return HttpResponse(job.destruction_time)

    @detail_route(methods=['get'])
    def error(self, request, pk):
        job = get_object_or_404(Job, pk=pk)
        return HttpResponse(job.error)

    @detail_route(methods=['get'])
    def quote(self, request, pk):
        job = get_object_or_404(Job, pk=pk)
        return HttpResponse(job.quote)

    @detail_route(methods=['get'])
    def owner(self, request, pk):
        job = get_object_or_404(Job, pk=pk)
        return HttpResponse(job.owner.username)
