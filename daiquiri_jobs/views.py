from rest_framework import viewsets

from .models import Job
from .serializers import JobSerializer
from .paginations import JobPagination


class JobsViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    pagination_class = JobPagination
