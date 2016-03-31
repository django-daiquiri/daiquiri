from django.core.urlresolvers import reverse

from daiquiri_uws.views import UWSViewSet

from .models import Job
from .serializers import JobsSerializer, JobSerializer


class JobsViewSet(UWSViewSet):
    queryset = Job.objects.all()
    list_serializer_class = JobsSerializer
    detail_serializer_class = JobSerializer

    def get_success_url(self):
        return reverse('uws:job-detail', kwargs=self.kwargs)
