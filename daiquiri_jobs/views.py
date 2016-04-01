from daiquiri_uws.views import UWSViewSet

from .models import Job
from .serializers import *


class JobsViewSet(UWSViewSet):
    queryset = Job.objects.all()
    list_serializer_class = JobsSerializer
    detail_serializer_class = JobSerializer
    detail_url_name = 'uws:job-detail'

class QueryJobsViewSet(JobsViewSet):
    queryset = Job.objects.filter(job_type=Job.JOB_TYPE_QUERY)
    detail_url_name = 'uws:query-detail'
